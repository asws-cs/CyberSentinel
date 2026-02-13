import asyncio
from typing import AsyncGenerator, List

from utils.logger import logger

class SubprocessStreamer:
    """
    Manages running a subprocess and streaming its stdout and stderr.
    """
    def __init__(self, command: List[str]):
        self.command = command
        self.process: asyncio.subprocess.Process | None = None

    async def start(self) -> AsyncGenerator[str, None]:
        """
        Starts the subprocess and yields its output line by line.
        """
        cmd_str = " ".join(self.command)
        logger.info(f"Starting streamed command: {cmd_str}")
        try:
            # Using create_subprocess_exec to execute the command directly
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if self.process.stdout is None or self.process.stderr is None:
                raise RuntimeError("Failed to get stdout/stderr streams from subprocess.")

            # Concurrently read from stdout and stderr
            async for line in self._stream_merged(self.process.stdout, self.process.stderr):
                yield line
            
            await self.process.wait()

        except Exception as e:
            error_msg = f"Error running streamed command '{cmd_str}': {e}"
            logger.error(error_msg)
            yield error_msg

    async def _stream_merged(self, *streams: asyncio.StreamReader) -> AsyncGenerator[str, None]:
        """
        Merges multiple asyncio streams and yields lines as they become available.
        """
        # Create a task for each stream to read lines
        tasks = {asyncio.create_task(s.readline()): s for s in streams}
        
        while tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                line_bytes = task.result()
                stream = tasks.pop(task)
                
                if line_bytes:
                    yield line_bytes.decode('utf-8', errors='replace').strip()
                    # Re-schedule the read task for the same stream
                    tasks[asyncio.create_task(stream.readline())] = stream
                
    async def terminate(self):
        """
        Terminates the running subprocess.
        """
        if self.process and self.process.returncode is None:
            cmd_str = " ".join(self.command)
            logger.info(f"Terminating process {self.process.pid} for command: {cmd_str}")
            try:
                self.process.terminate()
                await self.process.wait()
            except ProcessLookupError:
                logger.warning(f"Process {self.process.pid} already terminated.")
            except Exception as e:
                logger.error(f"Error terminating process {self.process.pid}: {e}")
