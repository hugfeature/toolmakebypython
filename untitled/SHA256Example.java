import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.logging.*;

public class SHA256Example {
    private static final Logger logger = Logger.getLogger(SHA256Example.class.getName());
    public static String getSHA256(String input) {
            // 配置日志输出级别
            logger.setLevel(Level.ALL);

            // 控制台输出
            ConsoleHandler handler = new ConsoleHandler();
            handler.setLevel(Level.ALL);
            logger.addHandler(handler);
        try {
            // 获取MessageDigest实例并指定算法为SHA-256
            MessageDigest md = MessageDigest.getInstance("SHA-256");

            // 将输入字符串转换为字节数组，并进行哈希计算
            byte[] hash = md.digest(input.getBytes());

            // 将字节数组转换为十六进制表示的字符串
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) sb.append('0');
                sb.append(hex);
            }

            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) {
        String miyao = "e108619297c2bd10891055da0a641e7d";
        // java >= 8
        Long timestamp = Instant.now().getEpochSecond();
        logger.log(Level.INFO,"时间戳是：{0},密钥是{1}", new Object[]{timestamp, miyao});
        String input = miyao + timestamp;
        logger.log(Level.INFO, "SHA-256:{0} ", getSHA256(input));
    }
}
