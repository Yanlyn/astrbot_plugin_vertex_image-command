import aiohttp
from pathlib import Path
from astrbot.api import logger


async def send_file(file_path: str, HOST: str = "localhost", PORT: int = 3658) -> str:
    """
    发送文件到远程服务器

    Args:
        file_path (str): 本地文件路径
        HOST (str): 服务器地址
        PORT (int): 服务器端口

    Returns:
        str: 远程文件路径，失败时返回原路径
    """
    try:
        url = f"http://{HOST}:{PORT}/upload"

        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field(
                    "file",
                    f,
                    filename=Path(file_path).name,
                    content_type="application/octet-stream",
                )

                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        remote_path = result.get("path", file_path)
                        logger.info(f"文件已上传到远程服务器: {remote_path}")
                        return remote_path
                    else:
                        logger.warning(
                            f"文件上传失败，状态码: {response.status}，使用本地路径"
                        )
                        return file_path

    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        return file_path

    except aiohttp.ClientError as e:
        logger.warning(f"网络请求错误: {e}，使用本地路径")
        return file_path

    except Exception as e:
        logger.error(f"发送文件时发生未预期的错误: {e}")
        return file_path
