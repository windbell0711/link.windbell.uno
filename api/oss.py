from datetime import timedelta
import alibabacloud_oss_v2 as oss2

# 1. 从环境变量读取密钥
credentials_provider = oss2.credentials.EnvironmentVariableCredentialsProvider()

# 2. 配置客户端
cfg = oss2.config.load_default()
cfg.credentials_provider = credentials_provider
cfg.region = 'cn-hongkong'

# 3. 创建客户端
client = oss2.Client(cfg)

# 4. 生成 OSS 预签名临时链接
def get_oss_url(bucket_name: str, object_key: str) -> str | None:
    result = client.presign(
        oss2.models.GetObjectRequest(bucket=bucket_name, key=object_key),
        expires=timedelta(minutes=30),
    )
    return result.url
