#!/usr/bin/env python3
"""
Система кэширования изображений для оптимизации производительности
"""

import os
import hashlib
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any

class ImageCache:
    def __init__(self, cache_dir: str = "image_cache", max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_hours = max_age_hours
        self.cache_index_file = os.path.join(cache_dir, "cache_index.json")
        self.cache_index = {}
        
        # Создаем директорию кэша если не существует
        os.makedirs(cache_dir, exist_ok=True)
        
        # Загружаем индекс кэша
        self._load_cache_index()
    
    def _load_cache_index(self):
        """Загружаем индекс кэша из файла"""
        try:
            if os.path.exists(self.cache_index_file):
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    self.cache_index = json.load(f)
                print(f"📁 Загружен индекс кэша: {len(self.cache_index)} записей")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки индекса кэша: {e}")
            self.cache_index = {}
    
    def _save_cache_index(self):
        """Сохраняем индекс кэша в файл"""
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения индекса кэша: {e}")
    
    def _get_cache_key(self, image_url: str) -> str:
        """Генерируем ключ кэша для URL изображения"""
        return hashlib.md5(image_url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Получаем путь к файлу кэша"""
        return os.path.join(self.cache_dir, f"{cache_key}.jpg")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверяем, действителен ли кэш"""
        if cache_key not in self.cache_index:
            return False
        
        cache_info = self.cache_index[cache_key]
        cache_time = datetime.fromisoformat(cache_info['timestamp'])
        max_age = timedelta(hours=self.max_age_hours)
        
        return datetime.now() - cache_time < max_age
    
    async def get_cached_image(self, image_url: str, auth_headers: dict = None) -> Optional[str]:
        """Получаем изображение из кэша или загружаем его"""
        cache_key = self._get_cache_key(image_url)
        
        # Проверяем, есть ли изображение в кэше
        if self._is_cache_valid(cache_key):
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                print(f"📁 Изображение найдено в кэше: {image_url}")
                return f"/cache/{cache_key}.jpg"
        
        # Загружаем изображение
        return await self._download_and_cache_image(image_url, cache_key, auth_headers)
    
    async def _download_and_cache_image(self, image_url: str, cache_key: str, auth_headers: dict = None) -> Optional[str]:
        """Загружаем изображение и сохраняем в кэш"""
        try:
            print(f"📥 Загружаем изображение: {image_url}")
            
            # Подготавливаем заголовки для запроса
            headers = {}
            if auth_headers:
                headers.update(auth_headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, headers=headers) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Сохраняем изображение в кэш
                        cache_path = self._get_cache_path(cache_key)
                        with open(cache_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Обновляем индекс кэша
                        self.cache_index[cache_key] = {
                            'url': image_url,
                            'timestamp': datetime.now().isoformat(),
                            'size': len(image_data),
                            'path': cache_path
                        }
                        self._save_cache_index()
                        
                        print(f"✅ Изображение загружено и сохранено в кэш: {len(image_data)} байт")
                        return f"/cache/{cache_key}.jpg"
                    else:
                        print(f"❌ Ошибка загрузки изображения: {response.status}")
                        # Если не удалось загрузить, возвращаем оригинальный URL
                        return image_url
                        
        except Exception as e:
            print(f"⚠️ Ошибка загрузки изображения {image_url}: {e}")
            # В случае ошибки возвращаем оригинальный URL
            return image_url
    
    def clear_expired_cache(self):
        """Очищаем устаревшие записи кэша"""
        expired_keys = []
        current_time = datetime.now()
        max_age = timedelta(hours=self.max_age_hours)
        
        for cache_key, cache_info in self.cache_index.items():
            cache_time = datetime.fromisoformat(cache_info['timestamp'])
            if current_time - cache_time > max_age:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
            del self.cache_index[cache_key]
        
        if expired_keys:
            self._save_cache_index()
            print(f"🗑️ Удалено {len(expired_keys)} устаревших записей кэша")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получаем статистику кэша"""
        total_size = sum(info.get('size', 0) for info in self.cache_index.values())
        return {
            'total_entries': len(self.cache_index),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }
