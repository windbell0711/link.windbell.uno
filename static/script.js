// const path = window.location.pathname;

// if (path.startsWith("/permanent/") && path.length > 11) {
//     const code = path.substring(11);
//     permanentRedirect(code);
// } else {
//     document.body.innerHTML = `<h2>不可能的分支</h2>`;
// }

// function permanentRedirect(code) {
//     fetch(`/api/redirect?code=${encodeURIComponent(code)}`)
//         .then(res => res.json())
//         .then(data => {
//             if (data.valid) {
//                 window.location.href = data.url;
//             } else {
//                 document.body.innerHTML = `<h2>链接无效或已过期</h2>`;
//             }
//         })
//         .catch(() => document.body.innerHTML = `<h2>服务异常，请稍后重试</h2>`);
// }
