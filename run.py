from transgptex.translate_tex import translate_single_tex
from transgptex.file_selector import select_file

if __name__ == "__main__":
    # translate_single_tex(r"C:\Python\趣味工具\MathTranslate_plus\MathTranslate\test_latex\input_accent.tex", ".", "Chinese")
    select_file(r"test_arxiv3", "output_glm3", "Chinese")