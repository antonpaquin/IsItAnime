FSIZE=$(stat --format=%s data.tar.gz)
aws s3api get-object \
            --bucket isitanime-data-archive \
            --key data.tar.gz \
            --range "bytes=$FSIZE-" \
            /dev/stdout | pv >> data.tar.gz
