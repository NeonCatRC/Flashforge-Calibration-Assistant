#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Модуль для управления SSH-соединениями с принтером

import paramiko
import os
import logging
import shlex
from typing import Tuple, Optional, Dict, List


class SSHConnectionManager:
    # Класс для управления SSH-соединениями

    def __init__(self, host: str = '', username: str = '', password: str = '', timeout: int = 10):
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None

    # Устанавливает SSH соединение
    def connect(self) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.host,
                username=self.username,
                password=self.password,
                timeout=self.timeout
            )
            return True
        except Exception as e:
            logging.error(f"SSH connection error: {str(e)}")
            return False

    # Закрывает соединение
    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    # Выполняет команду на удаленном сервере
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        if not self.client:
            if not self.connect():
                return -1, "", "Failed to establish SSH connection"

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')

            return exit_code, stdout_text, stderr_text
        except Exception as e:
            logging.error(f"Command execution error: {str(e)}")
            return -1, "", str(e)

    # Загружает файл с удаленного сервера
    def get_file(self, remote_path: str, local_path: str) -> bool:
        if not self.client:
            if not self.connect():
                return False

        try:
            from scp import SCPClient
            scp = SCPClient(self.client.get_transport())
            try:
                scp.get(remote_path, local_path)
                return True
            finally:
                scp.close()
        except Exception as e:
            logging.error(f"File download error: {str(e)}")
            return False

    # Ищет файлы по шаблону в удаленной директории
    def find_files(self, remote_dir: str, pattern: str) -> List[str]:
        command = f"find {shlex.quote(remote_dir)} -name {shlex.quote(pattern)} -type f"
        exit_code, stdout, _ = self.execute_command(command)

        if exit_code == 0:
            return [line.strip() for line in stdout.split('\n') if line.strip()]
        return []

    # Загружает файл конфигурации принтера
    def get_printer_config(self, remote_config_path: str, local_dir: str) -> Optional[str]:
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        local_path = os.path.join(local_dir, os.path.basename(remote_config_path))

        if self.get_file(remote_config_path, local_path):
            return local_path
        return None

    # Загружает файлы данных акселерометра для input shaper
    def get_shaper_data(self, local_dir: str) -> List[str]:
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        # Поиск файлов с данными акселерометра
        remote_files = self.find_files("/tmp", "calibration_data_*.csv")

        downloaded_files = []
        for remote_file in remote_files:
            local_path = os.path.join(local_dir, os.path.basename(remote_file))
            if self.get_file(remote_file, local_path):
                downloaded_files.append(local_path)

        return downloaded_files
