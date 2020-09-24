from enum import Enum


class ContractAddress(Enum):
    KyberNetwork = "0xd44B9352e4Db6d0640449ed653983827BD882885"
    KyberNetworkProxy = "0xd3add19ee7e5287148a5866784aE3C55bd4E375A"
    ConversionRates = "0x6E9b241Eec2C4a80485c1D2dF750231AFaf1A167"
    LiquidityConversionRates = "0x8b3BdEcEac3d23A215300A3df19e1bEe43A0Ac9C"
    SanityRates = "0xf71D305142eC1aC03896526D52F743959db01624"
    KyberReserve = "0x19F18bde9896890f161DeD31B05b58dc0ffD911b"
    KyberAutomatedReserve = "0xdE4e2118f45f1b27699B25004563819B57f5E3b2"
    KyberOrderbookReserve = "0x586F3cDCe25E76B69efD1C6Eb6104FAa0760A6a8"
    PermissionlessOrderbookReserveLister = "0x295631209354194B6453921bfFeFEe79cD42BdB9"
    FeeBurner = "0x63D556067eDbCD97ACc3356314398F70d4CcF948"
    WhiteList = "0x5a8665AbbDe3986687494176e22d38B169EA1eab"
    ExpectedRate = "0xB4c927fC102547e4089b02caE5E92d866F63bFE6"
    SwapEtherToToken = "0x47bC234Bf1F1436A794DF0a9FcA2935ea384629E"
    SwapTokenToEther = "0x6aBd125bcc68012197D81a92B4A56307177e0DBD"
    SwapTokenToToken = "0xB31b6edd85c386C259FB5488dae8Be4ed82C0778"
    Trade = "0x3f21DD3b2Aca23e495290a8dcb9A934984D93a6c"


class TokenAddress(Enum):
    ETH = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    KNC = "0x8c13AFB7815f10A8333955854E6ec7503eD841B7"
    OMG = "0x3750bE154260872270EbA56eEf89E78E6E21C1D9"
    SALT = "0x7ADc6456776Ed1e9661B3CEdF028f41BD319Ea52"
    ZIL = "0x400DB523AA93053879b20F10F56023b2076aC852"
    MANA = "0xe19Ec968c15f487E96f631Ad9AA54fAE09A67C8c"
    POLY = "0x58A21f7aA3D9D83D0BD8D4aDF589626D13b94b45"
    SNT = "0xA46E01606f9252fa833131648f4D855549BcE9D9"