#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1, description="Command to execute")
    timeout: Optional[int] = Field(30, ge=1, le=300, description="Timeout in seconds")


class CommandResponse(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    command: str
    execution_time: float


class Config:
    def __init__(self):
        self.sudo_password = os.getenv('SUDO_PASSWORD', '')
        self.port = int(os.getenv('PORT', 3000))
        self.config_file = 'config.json'
        self._load_config()
    
    def _load_config(self):
        """Загрузка конфигурации из файла или создание по умолчанию"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.sudo_password = config_data.get('sudoPassword', self.sudo_password)
                    self.port = config_data.get('port', self.port)
                logger.info("Configuration loaded from file")
            else:
                # Создаем конфигурацию по умолчанию
                default_config = {
                    'sudoPassword': '',
                    'port': self.port
                }
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.warning("Created default config file. Please update with your sudo password.")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise


class SudoManager:
    def __init__(self, password: str):
        self.password = password
    
    async def check_sudo_rights(self) -> bool:
        """Проверка наличия sudo прав без пароля"""
        try:
            process = await asyncio.create_subprocess_exec(
                'sudo', '-n', 'true',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def authenticate_sudo(self) -> bool:
        """Аутентификация sudo с паролем"""
        if not self.password:
            return False
            
        try:
            process = await asyncio.create_subprocess_exec(
                'sudo', '-S', 'true',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate(input=(self.password + '\n').encode())
            
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Sudo authentication failed: {e}")
            return False


class CommandExecutor:
    def __init__(self, sudo_manager: SudoManager):
        self.sudo_manager = sudo_manager
    
    async def execute(self, command: str, timeout: int = 30) -> CommandResponse:
        """Выполнение команды с обработкой sudo"""
        import time
        start_time = time.time()
        
        try:
            # Проверяем и при необходимости аутентифицируем sudo
            has_sudo = await self.sudo_manager.check_sudo_rights()
            if not has_sudo and self.sudo_manager.password:
                logger.info("Authenticating sudo...")
                auth_success = await self.sudo_manager.authenticate_sudo()
                if auth_success:
                    logger.info("Sudo authenticated successfully")
                else:
                    logger.warning("Sudo authentication failed")
            
            # Выполняем команду
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                
                return CommandResponse(
                    success=process.returncode == 0,
                    exit_code=process.returncode,
                    stdout=stdout.decode('utf-8', errors='replace').strip(),
                    stderr=stderr.decode('utf-8', errors='replace').strip(),
                    command=command,
                    execution_time=round(execution_time, 3)
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_time = time.time() - start_time
                
                return CommandResponse(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Command timeout after {timeout} seconds",
                    command=command,
                    execution_time=round(execution_time, 3)
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {e}")
            
            return CommandResponse(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                command=command,
                execution_time=round(execution_time, 3)
            )


# Инициализация приложения
config = Config()
sudo_manager = SudoManager(config.sudo_password)
command_executor = CommandExecutor(sudo_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 Starting Telegram Linux Server on port {config.port}")
    if not config.sudo_password:
        logger.warning("⚠️ No sudo password configured")
    yield
    # Shutdown
    logger.info("👋 Shutting down server...")

app = FastAPI(
    title="Telegram Linux Server",
    description="Server for executing terminal commands with sudo handling",
    version="2.0.1",
    lifespan=lifespan
)


@app.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Выполнить команду терминала"""
    logger.info(f"Executing command: {request.command[:50]}...")
    
    result = await command_executor.execute(
        request.command, 
        request.timeout
    )
    
    if not result.success:
        logger.warning(f"Command failed: {result.stderr}")
    
    return result


@app.get("/")
async def root():
    """Информация о сервере"""
    return {
        "name": "Telegram Linux Server",
        "version": "2.0.1",
        "description": "High-performance server for executing terminal commands with sudo handling",
        "framework": "FastAPI",
        "endpoints": {
            "POST /execute": "Execute terminal command",
            "GET /": "Server info",
            "GET /docs": "Interactive API documentation"
        }
    }


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    import time
    start_time = time.time()
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=config.port,
        reload=False,
        log_level="info"
    )
