"""
LaTeX Compiler MCP Tool for PDF generation
"""

import os
import asyncio
import subprocess
from typing import Optional
from pathlib import Path
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.mcp.latex_compiler")


class LaTeXCompilationError(Exception):
    """Raised when LaTeX compilation fails"""
    def __init__(self, message: str, error_details: str = ""):
        self.message = message
        self.error_details = error_details
        super().__init__(self.message)


class LaTeXCompilerMCPTool:
    """
    MCP Tool wrapper for LaTeX compilation
    Compiles .tex files to .pdf using pdflatex
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.use_mock = settings.USE_MOCK_MCP_TOOLS
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "LaTeX Compiler initialized",
            extra={
                "output_dir": self.output_dir,
                "use_mock": self.use_mock
            }
        )
    
    async def compile(
        self,
        tex_file_path: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Compile LaTeX file to PDF
        
        Args:
            tex_file_path: Path to .tex file
            output_filename: Optional output PDF filename (without extension)
        
        Returns:
            Path to generated PDF file
        
        Raises:
            LaTeXCompilationError: If compilation fails
        """
        logger.info(
            "Starting LaTeX compilation",
            extra={
                "tex_file": tex_file_path,
                "use_mock": self.use_mock
            }
        )
        
        try:
            if self.use_mock:
                return await self._mock_compile(tex_file_path, output_filename)
            else:
                return await self._real_compile(tex_file_path, output_filename)
        
        except Exception as e:
            logger.error(
                "LaTeX compilation failed",
                extra={
                    "tex_file": tex_file_path,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    async def _real_compile(
        self,
        tex_file_path: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Real pdflatex compilation
        """
        logger.debug(
            "Executing real LaTeX compilation",
            extra={"tex_file": tex_file_path}
        )
        
        # Validate input file exists
        if not os.path.exists(tex_file_path):
            raise LaTeXCompilationError(
                f"LaTeX file not found: {tex_file_path}"
            )
        
        # Determine output filename
        if output_filename is None:
            output_filename = Path(tex_file_path).stem
        
        pdf_output = os.path.join(self.output_dir, f"{output_filename}.pdf")
        
        try:
            # Run pdflatex
            result = await asyncio.create_task(
                self._run_pdflatex(tex_file_path, pdf_output)
            )
            
            if result.returncode != 0:
                raise LaTeXCompilationError(
                    "pdflatex compilation failed",
                    error_details=result.stderr.decode() if result.stderr else "Unknown error"
                )
            
            # Verify PDF was created
            if not os.path.exists(pdf_output):
                raise LaTeXCompilationError(
                    "PDF file was not created despite successful compilation"
                )
            
            logger.info(
                "LaTeX compilation successful",
                extra={
                    "tex_file": tex_file_path,
                    "pdf_output": pdf_output
                }
            )
            
            return pdf_output
        
        except subprocess.CalledProcessError as e:
            raise LaTeXCompilationError(
                "pdflatex command failed",
                error_details=str(e)
            )
    
    async def _run_pdflatex(self, tex_file: str, output_pdf: str):
        """Run pdflatex subprocess"""
        loop = asyncio.get_event_loop()
        
        # Get directory containing the tex file
        tex_dir = os.path.dirname(os.path.abspath(tex_file))
        
        # Run pdflatex
        process = await asyncio.create_subprocess_exec(
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={self.output_dir}",
            tex_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        class ProcessResult:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        return ProcessResult(process.returncode, stdout, stderr)
    
    async def _mock_compile(
        self,
        tex_file_path: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Mock LaTeX compilation for testing
        Creates a dummy PDF file
        """
        logger.debug(
            "Using mock LaTeX compilation",
            extra={"tex_file": tex_file_path}
        )
        
        # Simulate compilation delay
        await asyncio.sleep(1.0)
        
        # Determine output filename
        if output_filename is None:
            output_filename = Path(tex_file_path).stem
        
        pdf_output = os.path.join(self.output_dir, f"{output_filename}.pdf")
        
        # Create mock PDF (minimal valid PDF structure)
        mock_pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Mock Resume) Tj ET
endstream endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000247 00000 n
0000000341 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
430
%%EOF
"""
        
        # Write mock PDF to file
        Path(pdf_output).parent.mkdir(parents=True, exist_ok=True)
        with open(pdf_output, 'wb') as f:
            f.write(mock_pdf_content)
        
        logger.info(
            "Mock LaTeX compilation completed",
            extra={
                "tex_file": tex_file_path,
                "pdf_output": pdf_output
            }
        )
        
        return pdf_output
    
    def extract_latex_error(self, error_text: str) -> str:
        """
        Extract error message from LaTeX compilation log
        Useful for sending to LLM for self-correction
        """
        lines = error_text.split('\n')
        errors = []
        
        for i, line in enumerate(lines):
            if 'Error' in line or 'error' in line:
                # Get context around error
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                errors.append(context)
        
        return '\n\n'.join(errors) if errors else "Unknown LaTeX error"


# Singleton instance
_latex_compiler_tool = None


def get_latex_compiler_tool() -> LaTeXCompilerMCPTool:
    """Get LaTeX Compiler MCP tool instance"""
    global _latex_compiler_tool
    if _latex_compiler_tool is None:
        _latex_compiler_tool = LaTeXCompilerMCPTool()
    return _latex_compiler_tool
