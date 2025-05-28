import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from markitdown import MarkItDown
import uvicorn
from dotenv import load_dotenv
import os
import pathlib
import uuid
import logging
from langchain_openai import ChatOpenAI

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
OUTPUT_DIR = os.environ.get("MARKITDOWN_OUTPUT_PATH", ".")
VLM_MODEL_PATH = os.environ.get("VLM_MODEL_PATH", ".")
VLM_URL = os.environ.get("VLM_URL", ".")

# Initialize FastMCP server for MarkItDown (SSE)
mcp = FastMCP("markitdown")

@mcp.tool()
async def convert_to_markdown(uri: str) -> str:
    """Convert a resource described by an http:, https:, file: or data: URI to markdown"""
    logger.info(f"Called convert_to_markdown with args: uri={uri}")
    md = MarkItDown().convert_uri(uri).markdown
    # 儲存為 .txt
    out_dir = pathlib.Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    # 取 URI 最後段當檔名，否則用 uuid
    name = pathlib.Path(uri).stem if pathlib.Path(uri).stem else str(uuid.uuid4())
    filepath = out_dir / f"{name}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)
    return f"已成功轉換 {name}.txt 檔案到 {OUTPUT_DIR}\n"


@mcp.tool()
async def convert_directory_to_markdown(directory_path: str) -> str:
    """Convert all supported files in a directory to markdown and save them as txt files"""
    logger.info(f"Called convert_directory_to_markdown with args: directory_path={directory_path}")
    dir_path = pathlib.Path(directory_path)
    
    if not dir_path.exists() or not dir_path.is_dir():
        return f"錯誤: {directory_path} 不是有效的目錄路徑"
    
    out_dir = pathlib.Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    converted_files = []
    failed_files = []
    
    for file_path in dir_path.glob('*.*'):
        try:
            if file_path.is_file():
                file_uri = f"file://{file_path.absolute()}"
                md = MarkItDown().convert_uri(file_uri).markdown
                
                # 儲存為 .txt
                output_file = out_dir / f"{file_path.stem}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(md)
                
                converted_files.append(str(file_path.name))
        except Exception as e:
            failed_files.append(f"{file_path.name} (錯誤: {str(e)})")
    
    result = f"已成功轉換 {len(converted_files)} 個檔案到 {OUTPUT_DIR}\n"
    
    if converted_files:
        result += "\n成功轉換的檔案:\n" + "\n".join(f"- {f}" for f in converted_files)
    
    if failed_files:
        result += "\n\n轉換失敗的檔案:\n" + "\n".join(f"- {f}" for f in failed_files)
    
    return result


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# Main entry point
def main():
    import argparse

    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run MCP SSE-based MarkItDown server")

    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run the server with SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Port to listen on (default: 3001)"
    )
    args = parser.parse_args()

    if not args.sse and (args.host or args.port):
        parser.error("Host and port arguments are only valid when using SSE transport.")
        sys.exit(1)

    if args.sse:
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=args.host if args.host else "127.0.0.1",
            port=args.port if args.port else 3001,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()