const express = require('express');
const { spawn, exec } = require('child_process');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Загрузка конфигурации
let config = {};
try {
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {
        config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } else {
        console.warn('Config file not found. Creating default config...');
        config = {
            sudoPassword: '',
            port: 3000
        };
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('Default config created. Please update config.json with your sudo password.');
    }
} catch (error) {
    console.error('Error loading config:', error);
    process.exit(1);
}

const PORT = config.port || 3000;

// Функция для проверки sudo прав
const checkSudoRights = () => {
    return new Promise((resolve, reject) => {
        exec('sudo -n true', (error, stdout, stderr) => {
            if (error) {
                resolve(false); // Нужен пароль
            } else {
                resolve(true); // Права уже есть
            }
        });
    });
};

// Функция для ввода sudo пароля
const authenticateSudo = (password) => {
    return new Promise((resolve, reject) => {
        const process = spawn('sudo', ['-S', 'true'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        process.stdin.write(password + '\n');
        process.stdin.end();

        process.on('close', (code) => {
            if (code === 0) {
                resolve(true);
            } else {
                reject(new Error('Incorrect sudo password'));
            }
        });

        process.on('error', (error) => {
            reject(error);
        });
    });
};

// Основной endpoint для выполнения команд
app.post('/execute', async (req, res) => {
    const { command } = req.body;

    if (!command) {
        return res.status(400).json({
            success: false,
            error: 'Command is required'
        });
    }

    try {
        // Проверяем, нужны ли sudo права
        const hasSudoRights = await checkSudoRights();
        
        if (!hasSudoRights && config.sudoPassword) {
            console.log('Authenticating sudo...');
            await authenticateSudo(config.sudoPassword);
            console.log('Sudo authenticated successfully');
        }

        // Выполняем команду
        const childProcess = spawn('bash', ['-c', command], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        childProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        childProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        childProcess.on('close', (code) => {
            res.json({
                success: code === 0,
                exitCode: code,
                stdout: stdout.trim(),
                stderr: stderr.trim(),
                command: command
            });
        });

        childProcess.on('error', (error) => {
            res.status(500).json({
                success: false,
                error: error.message,
                command: command
            });
        });

        // Таймаут для команд (30 секунд)
        setTimeout(() => {
            if (!childProcess.killed) {
                childProcess.kill('SIGTERM');
                res.status(408).json({
                    success: false,
                    error: 'Command timeout (30 seconds)',
                    command: command
                });
            }
        }, 30000);

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            command: command
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Информация о сервере
app.get('/', (req, res) => {
    res.json({
        name: 'Telegram Linux Server',
        version: '1.0.0',
        description: 'Server for executing terminal commands with sudo password handling',
        endpoints: {
            'POST /execute': 'Execute terminal command',
            'GET /health': 'Health check',
            'GET /': 'Server info'
        }
    });
});

// Запуск сервера
app.listen(PORT, () => {
    console.log(`🚀 Telegram Linux Server running on port ${PORT}`);
    console.log(`📡 Health check: http://localhost:${PORT}/health`);
    console.log(`📋 API docs: http://localhost:${PORT}/`);
    
    if (!config.sudoPassword) {
        console.warn('⚠️  Warning: No sudo password configured. Update config.json if sudo commands are needed.');
    }
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down server...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n👋 Shutting down server...');
    process.exit(0);
});