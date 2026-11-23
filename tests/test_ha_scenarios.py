"""Scenarios in which Home Assistant uses the ADB connection concurrently.

They check that commands queue instead of being dropped, that a hanging command does not block the connection
forever, and that a command which waited for the connection is not sent once the connection has been closed.
"""

import asyncio
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, "..")

from androidtv.adb_manager import adb_manager_async, adb_manager_sync
from androidtv.adb_manager.adb_manager_async import ADBPythonAsync, ADBServerAsync
from androidtv.adb_manager.adb_manager_sync import ADBPythonSync, ADBServerSync
from androidtv.exceptions import LockNotAcquiredException
from androidtv.firetv.firetv_async import FireTVAsync

from . import async_patchers, patchers
from .async_wrapper import awaiter

PNG = b"\x89PNG\r\n\x1a\nDATA"


class SlowDeviceAsync(async_patchers.AdbDeviceTcpAsyncFake):
    """A fake device whose commands take some time, which records how many commands run at the same time."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay = 0.05
        self.calls = []
        self.running = 0
        self.max_running = 0
        self.hang = None
        self.connect_error = None

    async def connect(self, *args, **kwargs):
        await asyncio.sleep(self.delay)
        if self.connect_error:
            raise self.connect_error
        self.available = True

    async def shell(self, cmd, *args, **kwargs):
        self.calls.append(cmd)
        self.running += 1
        self.max_running = max(self.max_running, self.running)
        try:
            if self.hang is not None and cmd == "HANG":
                await self.hang.wait()
            await asyncio.sleep(self.delay)
        finally:
            self.running -= 1
        if cmd == "screencap -p":
            return PNG
        return ""


class TestHomeAssistantScenariosAsync(unittest.TestCase):
    """Concurrent use of a Fire TV device as in Home Assistant (update, screencap, services)."""

    def setUp(self):
        with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceTcpAsync", SlowDeviceAsync):
            self.ftv = FireTVAsync("HOST", 5555)
        self.device = self.ftv._adb._adb

    @awaiter
    async def test_concurrent_commands_are_queued(self):
        """Update, screencap, turn_on and a service command at the same time: none is dropped, one at a time."""
        self.assertTrue(await self.ftv.adb_connect())
        results = await asyncio.gather(
            self.ftv.update(),
            self.ftv.adb_screencap(),
            self.ftv.turn_on(),
            self.ftv.adb_shell("SERVICE"),
        )
        self.assertEqual(results[1], PNG)
        self.assertEqual(results[3], "")
        self.assertIn("screencap -p", self.device.calls)
        self.assertIn("SERVICE", self.device.calls)
        self.assertEqual(self.device.max_running, 1)
        self.assertFalse(self.ftv._adb._adb_lock.locked())

    @awaiter
    async def test_commands_run_in_order(self):
        """Queued commands run in the order in which they were sent."""
        self.assertTrue(await self.ftv.adb_connect())
        await asyncio.gather(*(self.ftv.adb_shell("CMD{}".format(i)) for i in range(5)))
        self.assertEqual(self.device.calls, ["CMD{}".format(i) for i in range(5)])

    @awaiter
    async def test_hanging_command_does_not_block_forever(self):
        """A command waits at most ``DEFAULT_LOCK_TIMEOUT_S`` behind a hanging one; then the connection recovers."""
        self.assertTrue(await self.ftv.adb_connect())
        self.device.hang = asyncio.Event()
        hanging = asyncio.create_task(self.ftv.adb_shell("HANG"))
        await asyncio.sleep(0.01)

        with patch.object(adb_manager_async, "DEFAULT_LOCK_TIMEOUT_S", 0.1):
            with self.assertLogs("androidtv.adb_manager.adb_manager_async", level="WARNING") as logs:
                with self.assertRaises(LockNotAcquiredException):
                    await self.ftv.adb_shell("NEXT")
        self.assertIn("busy for more than 0.1 seconds", logs.output[0])
        self.assertNotIn("NEXT", self.device.calls)

        self.device.hang.set()
        self.assertEqual(await hanging, "")
        self.assertEqual(await self.ftv.adb_shell("NEXT"), "")
        self.assertFalse(self.ftv._adb._adb_lock.locked())

    @awaiter
    async def test_command_queued_behind_failed_connect_is_not_sent(self):
        """The TV went to sleep: the connect fails, and a command that waited behind it is not sent."""
        self.assertTrue(await self.ftv.adb_connect())
        self.device.connect_error = OSError("unreachable")
        connect = asyncio.create_task(self.ftv.adb_connect(log_errors=False))
        await asyncio.sleep(0.01)
        self.assertIsNone(await self.ftv.adb_shell("AFTER"))
        self.assertFalse(await connect)
        self.assertNotIn("AFTER", self.device.calls)
        self.assertFalse(self.ftv.available)
        self.assertFalse(self.ftv._adb._adb_lock.locked())

    @awaiter
    async def test_cancelled_update_frees_the_connection(self):
        """Home Assistant cancels an update (e.g., on shutdown or timeout): the connection is free again."""
        self.assertTrue(await self.ftv.adb_connect())
        self.device.delay = 1.0
        update = asyncio.create_task(self.ftv.update())
        await asyncio.sleep(0.05)
        update.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await update
        self.assertFalse(self.ftv._adb._adb_lock.locked())
        self.device.delay = 0.0
        self.assertEqual(await self.ftv.adb_shell("NEXT"), "")


class TestRecheckAvailabilityAsync(unittest.TestCase):
    """A command that waited for the lock is not sent if the connection was closed in the meantime (async)."""

    @staticmethod
    def _make_unavailable(adb):
        if isinstance(adb, ADBPythonAsync):
            adb._adb.available = False
        else:
            adb._available = False

    async def _check(self, adb, method, args, device_method):
        await adb._adb_lock.acquire()
        task = asyncio.create_task(getattr(adb, method)(*args))
        await asyncio.sleep(0.01)
        self._make_unavailable(adb)
        with patch.object(adb._adb if isinstance(adb, ADBPythonAsync) else adb._adb_device, device_method) as sent:
            adb._adb_lock.release()
            self.assertIsNone(await task)
            sent.assert_not_called()
        self.assertFalse(adb._adb_lock.locked())

    @awaiter
    async def test_python(self):
        for method, args, device_method in (
            ("shell", ("TEST",), "shell"),
            ("screencap", (), "shell"),
            ("push", ("LOCAL", "DEVICE"), "push"),
            ("pull", ("LOCAL", "DEVICE"), "pull"),
        ):
            with self.subTest(method=method):
                with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)["python"]:
                    adb = ADBPythonAsync("HOST", 5555)
                    self.assertTrue(await adb.connect())
                await self._check(adb, method, args, device_method)

    @awaiter
    async def test_server(self):
        for method, args, device_method in (
            ("shell", ("TEST",), "shell"),
            ("screencap", (), "screencap"),
            ("push", ("LOCAL", "DEVICE"), "push"),
            ("pull", ("LOCAL", "DEVICE"), "pull"),
        ):
            with self.subTest(method=method):
                with async_patchers.patch_connect(True)["server"]:
                    adb = ADBServerAsync("HOST", 5555, "ADB_SERVER_IP")
                    self.assertTrue(await adb.connect())
                await self._check(adb, method, args, device_method)


class TestRecheckAvailabilitySync(unittest.TestCase):
    """A command that waited for the lock is not sent if the connection was closed in the meantime (sync)."""

    def _check(self, adb, method, args, device, device_method, make_unavailable):
        result = []
        adb._adb_lock.acquire()
        thread = threading.Thread(target=lambda: result.append(getattr(adb, method)(*args)))
        thread.start()
        time.sleep(0.05)
        make_unavailable()
        with patch.object(device, device_method) as sent:
            adb._adb_lock.release()
            thread.join(5)
            self.assertFalse(thread.is_alive())
            sent.assert_not_called()
        self.assertEqual(result, [None])
        self.assertFalse(adb._adb_lock.locked())

    def test_python(self):
        for method, args, device_method in (
            ("shell", ("TEST",), "shell"),
            ("screencap", (), "shell"),
            ("push", ("LOCAL", "DEVICE"), "push"),
            ("pull", ("LOCAL", "DEVICE"), "pull"),
        ):
            with self.subTest(method=method):
                with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)["python"]:
                    adb = ADBPythonSync("HOST", 5555)
                    self.assertTrue(adb.connect())

                def make_unavailable(adb=adb):
                    adb._adb.available = False

                self._check(adb, method, args, adb._adb, device_method, make_unavailable)

    def test_server(self):
        for method, args, device_method in (
            ("shell", ("TEST",), "shell"),
            ("screencap", (), "screencap"),
            ("push", ("LOCAL", "DEVICE"), "push"),
            ("pull", ("LOCAL", "DEVICE"), "pull"),
        ):
            with self.subTest(method=method):
                with patchers.patch_connect(True)["server"]:
                    adb = ADBServerSync("HOST", 5555, "ADB_SERVER_IP")
                    self.assertTrue(adb.connect())

                def make_unavailable(adb=adb):
                    adb._available = False

                self._check(adb, method, args, adb._adb_device, device_method, make_unavailable)

    def test_sync_lock_timeout_logs_warning(self):
        """The sync manager also gives up after ``DEFAULT_LOCK_TIMEOUT_S`` and logs a warning."""
        lock = threading.Lock()
        lock.acquire()
        try:
            with patch.object(adb_manager_sync, "DEFAULT_LOCK_TIMEOUT_S", 0.1):
                with self.assertLogs("androidtv.adb_manager.adb_manager_sync", level="WARNING") as logs:
                    with self.assertRaises(LockNotAcquiredException):
                        with adb_manager_sync._acquire(lock):
                            pass  # pragma: no cover
        finally:
            lock.release()
        self.assertIn("busy for more than 0.1 seconds", logs.output[0])


if __name__ == "__main__":
    unittest.main()
