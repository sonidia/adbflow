## 1. List devices

```bash
adb devices -l
```

output: List of devices attached
2285d50b40047ece device product:starlteks model:SM_G960N device:starlteks transport_id:1

👉 First column (2285d50b40047ece) is serial/ID.

## 2. Send request for special device

```bash
adb -s <serial/ID> shell monkey -p org.mozilla.firefox -c android.intent.category.LAUNCHER 1
```
