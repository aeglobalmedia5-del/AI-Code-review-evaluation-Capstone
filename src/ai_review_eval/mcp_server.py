"""Optional MCP server exposing the same file-reader and linter tools."""
from fastmcp import FastMCP
from .tools import FileReaderTool, LinterTool

mcp = FastMCP("AI Code Review MCP")
reader, linter = FileReaderTool(), LinterTool()

@mcp.tool()
async def read_code_file(filename: str, role: str = "reviewer") -> str:
    return await reader.read_file(filename, role)

@mcp.tool()
async def lint_code(filename: str, code: str, role: str = "reviewer") -> list[dict]:
    return await linter.lint(filename, code, role)

if __name__ == "__main__":
    mcp.run()
