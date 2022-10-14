
def assign_request(attrs):
    return {
        "modelName": attrs["modelName"],
        "modelAssigner": attrs["modelAssigner"],  # 改了这个
        "numberOfPeers": 100,
        "timeLimit": attrs["timeLimit"],  # 改动:变成定值了
        "trainDataConf": attrs["trainDataConf"],
        "evaluateDataConf": attrs["evaluateDataConf"],
        "restrict": attrs["restrict"]
    }