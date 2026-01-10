"""
配置管理模块

使用 pydantic-settings 从环境变量和 .env 文件加载配置。
这样可以避免硬编码，方便不同环境使用不同配置。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # Hacker News API
    hn_api_base: str = "https://hacker-news.firebaseio.com/v0"
    fetch_limit: int = 30
    request_timeout: int = 10

    # AI 关键词（逗号分隔）
    ai_keywords: str = "ai,artificial intelligence,machine learning,ml,deep learning,llm,gpt,openai,claude,chatgpt,neural"

    # 数据存储
    data_dir: str = "data"

    # 日志级别
    log_level: str = "INFO"

    # 数据库（阶段 2 使用）
    database_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略未定义的环境变量
    )

    @property
    def ai_keywords_list(self) -> list[str]:
        """将逗号分隔的关键词转为列表"""
        return [kw.strip().lower() for kw in self.ai_keywords.split(",")]


# 全局配置实例（单例模式）
settings = Settings()
