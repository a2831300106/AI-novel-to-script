"""AI 服务提供商

封装百度文心一言和阿里通义千问 API
"""
import json
import yaml
import httpx
import asyncio
from typing import Optional, Dict, Any
from app.config import settings


class AIProviderError(Exception):
    """AI 服务错误"""
    pass


class AIProvider:
    """AI 服务提供商"""

    def __init__(self, provider: Optional[str] = None):
        """初始化 AI 服务提供商

        Args:
            provider: 服务提供商名称（wenxin / qwen）
        """
        self.provider = provider or settings.ai_provider
        self.client = httpx.AsyncClient(timeout=60.0)

        # 初始化 API 配置
        if self.provider == "wenxin":
            self.api_key = settings.wenxin_api_key
            self.secret_key = settings.wenxin_secret_key
            self.access_token = None
        elif self.provider == "qwen":
            self.api_key = settings.qwen_api_key
        else:
            raise AIProviderError(f"不支持的 AI 服务提供商: {self.provider}")

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()

    async def chat(self, prompt: str, system: str = "") -> str:
        """发送聊天请求

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            str: AI 回复
        """
        if self.provider == "wenxin":
            return await self._chat_wenxin(prompt, system)
        elif self.provider == "qwen":
            return await self._chat_qwen(prompt, system)
        else:
            raise AIProviderError(f"不支持的 AI 服务提供商: {self.provider}")

    async def chat_with_json(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """发送聊天请求并解析 JSON 回复

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            Dict[str, Any]: JSON 解析结果
        """
        # 添加 JSON 格式要求
        json_prompt = f"{prompt}\n\n请以 JSON 格式输出，不要添加任何其他文字。"

        response = await self.chat(json_prompt, system)

        # 解析 JSON
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON 内容
            json_match = self._extract_json(response)
            if json_match:
                return json.loads(json_match)
            raise AIProviderError(f"无法解析 JSON 回复: {response}")

    async def chat_with_yaml(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """发送聊天请求并解析 YAML 回复

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            Dict[str, Any]: YAML 解析结果
        """
        # 添加 YAML 格式要求
        yaml_prompt = f"{prompt}\n\n请以 YAML 格式输出，不要添加任何其他文字。"

        response = await self.chat(yaml_prompt, system)

        # 解析 YAML
        try:
            # 尝试直接解析
            return yaml.safe_load(response)
        except yaml.YAMLError:
            # 尝试提取 YAML 内容
            yaml_match = self._extract_yaml(response)
            if yaml_match:
                return yaml.safe_load(yaml_match)
            raise AIProviderError(f"无法解析 YAML 回复: {response}")

    async def _chat_wenxin(self, prompt: str, system: str) -> str:
        """调用百度文心一言 API

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            str: AI 回复
        """
        # 获取 access_token
        if not self.access_token:
            self.access_token = await self._get_wenxin_access_token()

        # 构建请求
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={self.access_token}"

        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        if system:
            payload["messages"].insert(0, {"role": "system", "content": system})

        # 发送请求
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("result", "")
        except httpx.HTTPError as e:
            raise AIProviderError(f"文心一言 API 调用失败: {str(e)}")

    async def _get_wenxin_access_token(self) -> str:
        """获取百度文心一言 access_token

        Returns:
            str: access_token
        """
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"

        try:
            response = await self.client.post(url)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token", "")
        except httpx.HTTPError as e:
            raise AIProviderError(f"获取文心一言 access_token 失败: {str(e)}")

    async def _chat_qwen(self, prompt: str, system: str) -> str:
        """调用阿里通义千问 API

        Args:
            prompt: 用户输入
            system: 系统提示

        Returns:
            str: AI 回复
        """
        # 构建请求
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        }

        if system:
            payload["input"]["messages"].insert(0, {"role": "system", "content": system})

        # 发送请求
        try:
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("output", {}).get("text", "")
        except httpx.HTTPError as e:
            raise AIProviderError(f"通义千问 API 调用失败: {str(e)}")

    def _extract_json(self, text: str) -> Optional[str]:
        """从文本中提取 JSON 内容

        Args:
            text: 文本内容

        Returns:
            Optional[str]: JSON 内容
        """
        # 尝试提取 {} 包围的内容
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group()
        return None

    def _extract_yaml(self, text: str) -> Optional[str]:
        """从文本中提取 YAML 内容

        Args:
            text: 文本内容

        Returns:
            Optional[str]: YAML 内容
        """
        # YAML 通常以 key: value 格式开始
        import re
        # 尝试提取从第一个 key: 开始的内容
        match = re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:.*', text, re.MULTILINE)
        if match:
            # 从匹配位置开始提取
            start = match.start()
            return text[start:]
        return None


# 全局 AI 服务实例
ai_provider = None


async def get_ai_provider() -> AIProvider:
    """获取 AI 服务实例

    Returns:
        AIProvider: AI 服务实例
    """
    global ai_provider
    if ai_provider is None:
        ai_provider = AIProvider()
    return ai_provider