#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Модуль для интерполяции сетки стола для визуализации

import numpy as np
from scipy.interpolate import griddata, RectBivariateSpline


class MeshInterpolator:
    # Класс для интерполяции данных сетки стола

    def __init__(self, mesh_data: np.ndarray, x_count: int, y_count: int):
        self.mesh_data = mesh_data
        self.x_count = x_count
        self.y_count = y_count

    # Интерполяция сетки методом кубического сплайна
    def interpolate_cubic(self,
                          target_points: int = 100,
                          smooth: float = 0.1) -> tuple:
        # Создаем исходную сетку координат
        x = np.linspace(0, self.x_count - 1, self.x_count)
        y = np.linspace(0, self.y_count - 1, self.y_count)

        # Создаем интерполятор с помощью сплайнов
        interpolator = RectBivariateSpline(x, y, self.mesh_data, s=smooth)

        # Создаем точки для интерполированной сетки
        x_new = np.linspace(0, self.x_count - 1, target_points)
        y_new = np.linspace(0, self.y_count - 1, target_points)
        X_new, Y_new = np.meshgrid(x_new, y_new)

        # Получаем интерполированные значения
        Z_new = interpolator(x_new, y_new)

        return X_new, Y_new, Z_new

    # Интерполяция сетки через griddata
    def interpolate_grid(self,
                        target_points: int = 100,
                        method: str = 'cubic') -> tuple:
        # Создаем список координат точек и значений
        points = []
        values = []

        for i in range(self.x_count):
            for j in range(self.y_count):
                points.append([i, j])
                values.append(self.mesh_data[i, j])

        # Преобразуем в numpy arrays
        points = np.array(points)
        values = np.array(values)

        # Создаем новую, более плотную сетку для интерполяции
        grid_x, grid_y = np.mgrid[0:self.x_count-0.01:complex(0, target_points),
                                 0:self.y_count-0.01:complex(0, target_points)]

        # Интерполируем значения на новой сетке
        grid_z = griddata(points, values, (grid_x, grid_y), method=method)

        return grid_x, grid_y, grid_z

    # Применение сглаживания к интерполированным данным
    def apply_smoothing(self, z_data: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        # Нормализуем данные для сглаживания
        z_min, z_max = np.nanmin(z_data), np.nanmax(z_data)
        z_range = z_max - z_min
        if z_range == 0:
            return z_data.copy()
        normalized_data = (z_data - z_min) / z_range

        # Применяем экспоненциальное сглаживание
        smoothed_data = np.exp(alpha * normalized_data) / np.exp(alpha)

        # Возвращаем к исходному диапазону
        smoothed_data = smoothed_data * (z_max - z_min) + z_min

        return smoothed_data
