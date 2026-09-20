# 本地命令与 CI 保持一致，避免「本地能跑、CI 挂掉」。
.PHONY: build check serve clean all

PY ?= python3

build:
	$(PY) scripts/build_site.py \
		--input src/guide.md \
		--output dist \
		--title "行测六大模块" \
		--subtitle "考点 / 技巧 / 例题" \
		--logo "行测" \
		--quiz-re '^\*\*示例\s*(\d+)\*\*(.*)$$' \
		--download "xingce-guide.docx" \
		--download-label "下载 Word 版"
	cp src/guide.docx dist/xingce-guide.docx

check:
	$(PY) scripts/check_site.py dist/index.html

serve: build
	cd dist && $(PY) -m http.server 8080

all: build check

clean:
	rm -rf dist
