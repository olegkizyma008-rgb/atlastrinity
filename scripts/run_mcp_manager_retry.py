#!/usr/bin/env python3
import asyncio
import errno

from src.brain.mcp_manager import MCPManager


async def test_restart_retry_success():
    manager = MCPManager()
    manager.config = {"mcpServers": {"foo": {"command": "python3", "args": ["-c", "pass"]}}}
    calls = {"n": 0}

    async def fake_connect(server_name, cfg):
        calls["n"] += 1
        if calls["n"] < 3:
            raise OSError(errno.EAGAIN, "Resource temporarily unavailable")
        return object()

    manager._connect_server = fake_connect
    res = await manager.restart_server("foo")
    print("test_restart_retry_success ->", res, "calls=", calls["n"])


async def test_restart_retry_fail():
    manager = MCPManager()
    manager.config = {"mcpServers": {"bar": {"command": "python3", "args": ["-c", "pass"]}}}
    manager._max_restart_attempts = 3

    async def always_fail(server_name, cfg):
        raise OSError(errno.EAGAIN, "Resource temporarily unavailable")

    manager._connect_server = always_fail
    res = await manager.restart_server("bar")
    print("test_restart_retry_fail ->", res)


async def run():
    await test_restart_retry_success()
    await test_restart_retry_fail()


if __name__ == "__main__":
    asyncio.run(run())
