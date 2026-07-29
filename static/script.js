const path = window.location.pathname;
const code = path.substring(1); // 去掉开头的 '/'
if (code) {
    fetch(`/api/redirect?code=${encodeURIComponent(code)}`)
        .then(res => res.json())
        .then(data => {
            if (data.valid) {
                window.location.href = data.url;
            } else {
                document.body.innerHTML = `<h2>链接无效或已过期</h2>`;
            }
        })
        .catch(() => document.body.innerHTML = `<h2>服务异常，请稍后重试</h2>`);
} else {
    document.body.innerHTML = `<h2>请在浏览器地址栏输入链接</h2>`;
}