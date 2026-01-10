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

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/hackernews.db"  # 异步 URL（应用使用）
    sync_database_url: str = "sqlite:///./data/hackernews.db"  # 同步 URL（Alembic 使用）
    db_echo: bool = False  # 是否打印 SQL 语句

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
