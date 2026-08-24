#!/usr/bin/env python3
"""Concurrency guard regression tests for the runtime compatibility layer."""

from __future__ import annotations

import inspect
import threading
import unittest

import ops_policy_runtime as runtime


class RuntimeConcurrencyTests(unittest.TestCase):
    def test_resolve_compatibility_overrides_are_lock_guarded(self) -> None:
        self.assertTrue(hasattr(runtime, "_RESOLVE_LOCK"))
        source = inspect.getsource(runtime.resolve)
        self.assertIn("with _RESOLVE_LOCK", source)

    def test_lock_is_reentrant_for_nested_runtime_helpers(self) -> None:
        lock = runtime._RESOLVE_LOCK
        self.assertTrue(lock.acquire(timeout=1.0))
        try:
            self.assertTrue(lock.acquire(timeout=1.0))
            lock.release()
        finally:
            lock.release()

    def test_guard_serializes_two_callers(self) -> None:
        entered = threading.Event()
        release = threading.Event()
        acquired_second = threading.Event()

        def first() -> None:
            with runtime._RESOLVE_LOCK:
                entered.set()
                release.wait(timeout=2.0)

        def second() -> None:
            entered.wait(timeout=2.0)
            with runtime._RESOLVE_LOCK:
                acquired_second.set()

        one = threading.Thread(target=first)
        two = threading.Thread(target=second)
        one.start()
        self.assertTrue(entered.wait(timeout=1.0))
        two.start()
        self.assertFalse(acquired_second.wait(timeout=0.05))
        release.set()
        one.join(timeout=1.0)
        two.join(timeout=1.0)
        self.assertTrue(acquired_second.is_set())
        self.assertFalse(one.is_alive())
        self.assertFalse(two.is_alive())


if __name__ == "__main__":
    unittest.main()
