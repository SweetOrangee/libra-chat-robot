# 生成带时间戳的日志文件名（格式：output_YYYYMMDD_HHMMSS.log）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="log/output_${TIMESTAMP}.log"

# 执行命令并将输出（包括stdout和stderr）重定向到日志文件
echo "Starting task... Log will be saved to: ${LOG_FILE}"
nb run &> "${LOG_FILE}"

# 执行结束后提示
echo "Task finished. Check log: ${LOG_FILE}"

