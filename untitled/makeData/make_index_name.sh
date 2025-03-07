#!/bin/bash

base_index_name="test"

for ((i=0; i<100; i++))
do
    start_date="2023-06-25"
    for ((j=0; j<180; j++))
    do
      current_date=$(date -d "$start_date -$j days" +%Y-%m-%d)
      timestamp=$(date -d "$current_date" +%s)
      millisecond_timestamp=$(expr "$timestamp" \* 1000)
      echo "$millisecond_timestamp"
      DATA="{\"attack_type\": \"file_inclusion\",
                         \"start_time\": $current_date,
                         \"level\": \"high\",
                         \"tenant_key\": \"jiao001.test121.com\",
                         \"tenant_id\": \"csp22b18-2285-4cee-aab7-a106f9de46a3\",
                         \"event_typeid\": \"1e03f836b1ff437f8f2c78b88cf8205e\",
                         \"timestamp\": $millisecond_timestamp,
                         \"src_ip\": \"100.120.194.177\",
                         \"dst_ip\": \"10.189.7.91\",
                         \"src_zone\": \"US\",
                         \"src_port\": \"38130\",
                         \"dst_port\": \"80\",
                         \"message\": \"  \",
                         \"url\": \"/faq.php?show=/etc/passwd0026c=guidelines\",
                         \"action\": \"deny\",
                         \"protocol_application\": \"http\",
                         \"payload\": \"payload\",
                         \"http_hostname\": \"jiao001.test121.com\",
                         \"http_referer\": \"http://www.baidu.com\",
                         \"http_cookies\": \"cookie\",
                         \"http_response_code\": \"200\",
                         \"http_ua\": \"Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0 Zerolab-P/v3.2\",
                         \"http_request_header\": \"GET /faq.php?show=/etc/passwd0026c=guidelines HTTP/1.1 RemoteIp: \"
                                                \"121.4.176.242 Host: qywx.saicmotor.com X-Forwarded-For: 121.4.176.242 \"
                                                \"Connection: close Accept-Encoding: identity Accept-Language: zh-CN,\"
                                                \"zh;q=0.8 Accept: */* User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:5.0) \"
                                                \"Gecko/20100101 Firefox/5.0 Zerolab-P/v3.2 Accept-Charset: GBK,utf-8;q=0.7,\"
                                                \"*;q=0.3 Zerolab-Scan: Zerolab-P/v3.2 Referer: http://www.baidu.com \"
                                                \"Cache-Control: max-age=0  \",
                         \"http_request_body\": \"body\",
                         \"http_response_header\": \"resp_header_raw\",
                         \"http_response_body\": \"resp_body\",
                         \"event_method\": \"GET\",
                         \"logsource_type\": \"WAF\",
                         \"event_uuid\": \"5a161458-e594-4114-b2e0-db46505029f2\",
                         \"raw_log_charset\": \"utf-8\",
                         \"logsource_name\": \"WAF\",
                         \"logsource_category\": \"event\",
                         \"logsource_ip\": \"10.141.206.252\",
                         \"logsource_timestamp\": \"1686560433099\",
                         \"raw_log\": \"<3>Aug1521:01:56waf-manager01safeline_event[1]:{\"action\":\"deny\",\"
                                    \"\"attack_type\":\"file_inclusion\",\"body\":\"body\",\"cookie\":\"cookie\",\"
                                    \"\"country\":\"US\",\"decode_path\":\"decode_path\",\"dest_ip\":\"10.189.7.91\",\"
                                    \"\"dest_port\":80,\"event_id\":\"1e03f836b1ff437f8f2c78b88cf8205e\",\"
                                    \"\"host\":\"jiao001.test121.com\",\"location\":\"location\",\"method\":\"GET\",\"
                                    \"\"module\":\"m_file_include\",\"node\":\"iZuf6ho87xfx35s7ozs06oZ\",\"
                                    \"\"payload\":\"payload\",\"protocol\":\"http\",\"province\":\"province\",\"reason\":\"  \"
                                    \"\",\"referer\":\"http://www.baidu.com\",\"req_header_raw\":\"GET \"
                                    \"/faq.php?show=/etc/passwd0026c=guidelines HTTP/1.1 RemoteIp: 121.4.176.242 Host: \"
                                    \"qywx.saicmotor.com X-Forwarded-For: 121.4.176.242 Connection: close Accept-Encoding: \"
                                    \"identity Accept-Language: zh-CN,zh;q=0.8 Accept: */* User-Agent: Mozilla/5.0 (Windows NT \"
                                    \"5.1; rv:5.0) Gecko/20100101 Firefox/5.0 Zerolab-P/v3.2 Accept-Charset: GBK,utf-8;q=0.7,\"
                                    \"*;q=0.3 Zerolab-Scan: Zerolab-P/v3.2 Referer: http://www.baidu.com Cache-Control: \"
                                    \"max-age=0  \",\"resp_body\":\"resp_body\",\"resp_header_raw\":\"resp_header_raw\",\"
                                    \"\"resp_reason_phrase\":\"resp_reason_phrase\",\"resp_status_code\":\"200\",\"
                                    \"\"risk_level\":\"high\",\"rule_id\":\"m_file_include\",\"selector_id\":\"selector_id\",\"
                                    \"\"session\":\"session\",\"src_ip\":\"100.120.194.177\",\"src_port\":38130,\"
                                    \"\"timestamp\":1660568516,\"timestamp_human\":\"2022-08-15 21:01:56\",\"
                                    \"\"urlpath\":\"/faq.php?show=/etc/passwd0026c=guidelines\",\"user_agent\":\"Mozilla/5.0 (\"
                                    \"Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0 Zerolab-P/v3.2\"} \"}"
          echo "$DATA"
#      index_tennat=$base_index_name-$i
#      index_name=$index_tennat-$current_date
#      echo "$index_name"

    done
done
