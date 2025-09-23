import re


def test_for_markdown_link(text):
    for i in range(len(text)):
        if text[i] == "[":
            for j in range(i, len(text)):
                if text[j] == "]":
                    if len(text) > j + 1 and text[j + 1] == "(":
                        for k in range(j + 1, len(text)):
                            if text[k] == ")":
                                return (i, k)
    return False


def split_then_markdownify(text):
    if test_for_markdown_link(text):
        i, k = test_for_markdown_link(text)
        return (
            split_then_markdownify(text[:i])
            + text[i: k + 1]
            + split_then_markdownify(text[k + 1:])
        )
    else:
        return convert_to_markdown(text)


def convert_to_markdown(text):
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    markdown_pattern = r"\[.*?\]\(.*?\)"
    url_regex = re.compile(url_pattern)
    markdown_regex = re.compile(markdown_pattern)

    def replace_url(match):
        url = match.group()
        if not markdown_regex.match(url):
            markdown_url = f"[{url}]({url})"
            return markdown_url
        else:
            return url

    text = url_regex.sub(replace_url, text)
    return text
