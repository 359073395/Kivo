# 印尼仓库SKU与价格当前资料

当前版本：2026-10-12，用户指定替换9.12仓库源；旧版只用于追溯。价格2现按用户同日后续指定的在线Y表读取，见当前源指针和在线Y来源卡。

- [来源卡](../../资源/来源索引/2026-10-12_印尼仓库SKU价格来源卡.md)
- [当前源指针](../../skill/tiktok-commerce-operations/references/current-warehouse-source.json)
- 正式源：tiktokSkuRoot/02_SKU定价源/10.12印尼所有产品及定价.xlsx。
- SHA-256：`a07d07086cd1bef236232de1667646dca03fa4da16aca3fdcbc51a9cc169efd3`。
- Sheet1第1行表头，888条SKU记录、887个精确SKU；Japan Lipoma Patch第56/57行重复同价。
- B是SKU、C为中文或原备注、D虾皮普店价、E猫店价、F/G附加备注。表内图片未逐一核验。
- 原791个SKU猫店价格未变，新增96个SKU；这96个全部缺Y仓活动价，最终活动价暂不可用。
- 价格1=(E+8000)*1.05向上取整，再与Y仓活动价取低；E已含3000，不重复加；Npcs按基础最终单件价*N。
- 商品是否真实在售、预购状态及线上活动价不能由本仓库源推断。源表清仓/作废/库存文字保留作状态，不直接执行线上动作。
- 同日先仅替换仓库源时，530条Flash无变化；随后用户采用在线Y价格，17条已改、38条待确认、475条无需变。店铺商品事实仍为2026-10-09导出。

## 全量SKU文字与价格快照

|源行|SKU|中文名称/原备注|虾皮普店价|猫店参考价|附加备注|
|---:|---|---|---|---|---|
|2|Hair film|仙蒂奈儿 发膜|43000|46000||
|3|Coat Milk|山羊沐浴露|45000|48000||
|4|Supple Ginger Senana|生姜洗发露|37000|40000||
|5|LUFUSHA BODY MUD|黎芙莎火山泥|38000|41000||
|6|FANSHILIN CREAM|黎芙莎身体霜|32000|35000||
|7|Seaweed LIFUSHA Sampo|黎芙莎海盐洗发水|46000|49000||
|8|Toothache Spray|牙痛宁|30000|33000||
|9|DISAPPEARS SCAR|疤痕一抹消|32000|35000||
|10|VIKADA Purple Shampoo|祛黄洗发水|40000|43000||
|11|Japan Cherry Cream|身体素颜霜|20000|20000||
|12|Joint Bone Therapy|骨骼霜|32000|35000||
|13|BAOJIANGAO|脂肪瘤|35000|38000||
|14|Sudocrem|婴儿屁屁霜|60000|63000||
|15|WHITE SHOES|小白鞋清洗剂|35000|38000||
|16|ZB GOUT|痛风膏|35000|38000||
|17|Morning Cherry Toothpaste|早安牙膏|检查是否还有库存|检查是否还有库存||
|18|SADOER-Slimming cream|SADOER纤体塑形霜|35000|38000||
|19|SADOER-Retinol FIRMING|视黄醇眼霜|40000|43000||
|20|SADOER Blue Teeth|SADOER牙粉|32000|35000||
|21|SADOER Collagen Cream|SADOER胶原面霜|35000|38000||
|22|Baizhentan Anti-freckle|百珍堂祛斑霜|35000|38000||
|23|Nail Repair Sumifun|Sumifun指甲修复膏|32000|35000||
|24|Orange SLIM PATCH|减肥贴|36000|39000||
|25|South Moon PsoriasisSolution|皮肤藓药膏|33000|36000||
|26|50g Varicose Vein|50g静脉曲张|33000|36000||
|27|eelhoe Bettel Nail|指甲修护液|33000|36000||
|28|Blue GENNTAL WARTS|South Moon克疣膏|33000|36000||
|29|NATURAL RAPID GROUWTH|头发生长液|32000|35000||
|30|South Lipoma Remover|South Moon脂肪膏|35000|38000||
|31|Japan ZXQC|抗皱紧致面霜|33000|36000||
|32|ADVANCED BEAUTY CURVE|纤体塑形霜|37000|40000||
|33|TAG&WART Remover|EELHOE皮肤去痣祛疣笔|32000|35000||
|34|Horse Oil CINDYNAL|马油|32000|35000||
|35|Dermatix|药膏|33000|36000||
|36|Yellow Ginger Patch|艾草贴|37000|40000||
|37|MQ Corn Pads|鸡眼贴|37000|40000||
|38|Sleep Aid Patch|睡眠贴|30000|33000||
|39|XOERMIOY HORSE OIL|雪弥马油|35000|38000||
|40|XOERMIOY Toothpaste|烟酰胺美白牙膏|38000|41000||
|41|SHAMPOO GINBI COCOA|GINBI洗发水|30000|33000||
|42|Conditoner GINBI COCOA|GINBI护发素|30000|33000||
|43|LUODAIS SALON|香水喷雾|38000|41000||
|44|Delicate Pink|娇润粉嫩霜|36000|39000||
|45|Coconut Body Lotion|椰子滋润身体|40000|43000||
|46|SADOER Boseine Cream|上朵山羊奶霜|38000|41000||
|47|SADOER Bamboo Charcoal|SADOER竹炭美白牙膏|15000|18000||
|48|Beard Care Serum|胡子护理精华液|37000|40000||
|49|Aloe Vera Hair Mask|芦荟发膜|45000|48000||
|50|Retinol Coffeine Cream|SADOER抗皱面霜|30000|33000||
|51|SADOER Coffeine Essence|SADOER抗皱精华液|30000|33000||
|52|ZOZU HOT Slimming|ZOZU纤体瘦身霜|38000|41000||
|53|GISEELAN Honey|黄金修护面膜|15000|18000||
|54|Sumifun Vitiligo|Sumifun白斑霜|35000|38000||
|55|Qinfeiyan Shampoo|何首乌洗发液|40000|43000||
|56|Japan Lipoma Patch|脂肪留贴|15000|18000||
|57|Japan Lipoma Patch|脂肪留贴|15000|18000||
|58|Japan toothache|牙龈痛喷剂|15000|18000||
|59|377 Cream|77祛斑霜|15000|18000||
|60|GET RID FAT|40pcs减肥贴|35000|38000||
|61|South Nail Ointmen|南月指甲膏|33000|36000||
|62|South hemorrhoid spray|痔疮喷雾|33000|36000||
|63|OUHOE Yellow Oil|黄色去角质油|35000|38000||
|64|Jaysuing Varicose Cream|jaysuing静脉曲张|33000|36000||
|65|OUHOE Scar Cream|祛疤膏|35000|38000||
|66|South Ear Ringing|耳鸣精华液|32000|35000||
|67|Growth Essential Oil|增高精油|15000|18000||
|68|EELHOE Ginger hair|头发生长喷雾|15000|18000||
|69|South Ginger Patch|南月减肥贴|15000|18000||
|70|South Varicose Spray|静脉曲张喷雾|15000|18000||
|71|Red Genital Warts|南月湿疣|33000|36000||
|72|Skin Tags Pen|EELHOE祛疣笔|15000|18000||
|73|Rose Cleansing|祛疣精华|33000|36000||
|74|30X VC|泰国VC精华|55000|58000||
|75|Doctor Anti-aging|Dorctor面霜|30000|33000||
|76|Small Brown Eye|小棕瓶眼霜|35000|38000||
|77|PINK Vase|凡士林身体乳|43000|46000||
|78|Intensive ​Care Vaseline|凡士林身体乳|43000|46000||
|79|3X UV Vaseline|凡士林身体乳|43000|46000||
|80|SPF 24 Vaseline|凡士林身体乳|43000|46000||
|81|一4℃ Vaseline|凡士林身体乳|43000|46000||
|82|Night Repair Vaseline|凡士林身体乳|43000|46000||
|83|Perfect 10 Vaseline|凡士林身体乳|43000|46000||
|84|CPIP Jifengtang|云南本草美白祛斑霜|15000|18000||
|85|Peach XOERMIOY|蜜桃身体乳|15000|18000||
|86|ZB Eye Drops|眼药水|35000|38000||
|87|RongYao Cleanser|男士洗面奶|40000|43000||
|88|ALASKA VOLCANO|清洁泥膜|45000|48000||
|89|MUGWORT|清洁绿膜|45000|48000||
|90|SWAN SECRET|日本痔疮膏|36000|39000||
|91|SADOER Enlarg Breast|上朵丰胸霜|37000|40000||
|92|Lotion Collagen SADOER|上朵胶原身体乳|38000|41000||
|93|Serum Collagen SADOER|上朵胶原精华|30000|33000||
|94|Toner Collagen SADOER|上朵胶原爽肤水|48000|51000||
|95|APDMP XI GAI|膝盖喷雾|30000|33000||
|96|Bait Red|钓鱼饵料|35000|38000||
|97|Sewer Liquid|管道疏通|35000|38000||
|98|ORANGE EXFOLIATING|黎芙莎去角质|15000|18000||
|99|Glutathione|谷胱甘肽软胶囊|95000|98000||
|100|ZOOSON-Freckle|SADOER美白祛斑霜|15000|18000||
|101|SADOER-Snail Eye|蜗牛眼霜|15000|18000||
|102|Yeleow Pasjel|Pasjel泰国妊娠霜|15000|18000||
|103|DSIUAN|蒂诗颜祛斑精华|20000|23000||
|104|LIFTHENG Cleanser|莉芙泉洗面奶|15000|18000||
|105|Lumbar Cold|腰椎冷敷凝胶|15000|18000||
|106|LAOLISHI Collagen|劳丽诗胶原霜|36000|39000||
|107|Dragon Blood|贵妇膏50g|32000|35000||
|108|Black ACVIAR Mask|鱼子酱发膜|42000|45000||
|109|GLUTA WHITENING|黎芙莎修护面霜|30000|33000||
|110|SAKURA GLOW|泰国VC精华|30000|33000||
|111|Yan Qi|妍绮润发精华乳|36000|39000||
|112|Hitam Rambut|一支黑|60000|63000||
|113|JIAN QIAO YAN|腱鞘关节喷剂|15000|18000||
|114|Green Eczema|湿毒清软膏|15000|18000||
|115|KIRKLAND MIN|Kirkland头发滴瓶|75000|78000||
|116|Veteran NANO|汽车镀膜剂手喷|52000|55000||
|117|Pink Sleek Stick|头发定型膏|33000|36000||
|118|Soda+SeaSalt|小苏打牙膏|33000|36000||
|119|NJ Headlight|大灯修复剂|45000|48000||
|120|XML 9H Car|镀膜剂|55000|58000||
|121|EE 10 Seconds|EE 腋下美白|15000|18000||
|122|INNER THIGHS|OUHOE 皮肤亮白霜|15000|18000||
|123|OUHOE Wart|OUHOE 克疣膏|15000|18000||
|124|MAN COLLAGEN|男士面霜|15000|18000||
|125|EE Retinol|EE 美肤霜|35000|38000||
|126|MYTHIC OIL|头发精油|38000|41000||
|127|Hair Straightener|直发器|110000|113000||
|128|RUOMO|若陌洗发水|48000|51000||
|129|ANTI-ACNE|冬奈儿亮肤祛痘膏|30000|33000||
|130|TM Drop Eye|眼博士滴眼液|32000|35000||
|131|HEM VC|VC精华|15000|18000||
|132|Sulfur XUERMI|硫磺沐浴露|36000|39000||
|133|Rat Repellent Spray|驱鼠喷雾|38000|41000||
|134|OMELIN PRETTY|龙血膏|50000|53000||
|135|CHONG SHU WAN|驱鼠樟脑丸|35000|38000||
|136|Salt Soap|海盐皂|15000|18000||
|137|RETINOL REPAIR|上朵视黄醇精华|15000|18000||
|138|Snake Venom Cream|SADOER紧致眼霜|35000|38000||
|139|ZOZU CUCUMBER|ZOZU脱毛膏|36000|39000||
|140|EYEBROW GROWTH|补鞋胶|36000|39000||
|141|JUE-FISH GLUE|眉毛增长|33000|36000||
|142|BAKING SODA|SKAT牙膏|15000|18000||
|143|Dahvernas MAGIC|卸甲油|30000|33000||
|144|Liquid Tooth|液体牙膏|40000|43000||
|145|YOUBUY BLEMISH|YOUBUY祛斑霜|已清仓-下架|已清仓-下架||
|146|MILK Moisturizing|牛奶沐浴露|已清仓-下架|已清仓-下架||
|147|Meniscus Pain|蜂毒乳膏|35000|38000||
|148|Red CAHNSAI|红色美白祛斑霜|已清仓-下架|已清仓-下架||
|149|BAIXUANGAO|百癣膏|32000|35000||
|150|ZTL JAPAN Butt|正泰林痔疮膏|30000|33000||
|151|Bosuya Centella|洗发膏|42000|45000||
|152|Big Head Bird|大头鸟儿童牙膏|38000|41000||
|153|JLUP Truffle|白松露沐浴露|42000|45000||
|154|Tinnidrop Spray|耳鸣喷雾|35000|38000||
|155|COLD GEL SPRAY|冷敷喷雾|15000|18000||
|156|CERVICAL SPRAY|腰椎喷雾|15000|18000||
|157|ICE HYDRA MOIST|冰晶面膜|15000|18000||
|158|Seawater Nasal Spray|海水鼻舒喷雾|35000|38000||
|159|V-shaped Tape|提脸贴|36000|39000||
|160|Black Sink Faucet|黑色立式式水龙头|已清仓-下架|已清仓-下架||
|161|Black Wall Faucet|黑色入墙式水龙头|已清仓-下架|已清仓-下架||
|162|Sink Horn|喇叭立式|已清仓-下架|已清仓-下架||
|163|Wall Horn|喇叭入墙式|已清仓-下架|已清仓-下架||
|164|Black 90°Square|黑色七字直角|已清仓-下架|已清仓-下架||
|165|Sliver 90°Square|银色七字直角|已清仓-下架|已清仓-下架||
|166|Sliver Faucet Sprayer|银色马桶喷枪套装|120000|123000||
|167|Black Faucet Sprayer|黑色马桶喷枪套装|120000|123000||
|168|Sliver Pull Keran|银色抽拉水龙头|200000|203000||
|169|Black Pull Keran|黑色抽拉水龙头|200000|203000||
|170|CERAMIDE Milk Plus|牛奶洗面奶|36000|39000||
|171|Red Japan Mask|日本发膜|45000|48000||
|172|SADOER Red DRAGON|龙血精华液|15000|18000||
|173|SADOER Collagen SAKURA|樱花精华液|37000|40000||
|174|Mint Oral Spray|口腔喷雾|30000|33000||
|175|VE Moist Lotion|维生素E乳|15000|18000||
|176|SADOER VLIFT CREAM|V脸|34000|37000||
|177|SADOER Repair Scar|SADOER疤痕霜|15000|18000||
|178|SADOER CASTOR OIL|睫毛增长油|35000|38000||
|179|Butt ENRICHING|丰臀霜|35000|38000||
|180|YIMIOSI NIA|烟酰胺面霜|15000|18000||
|181|Battery Repair|电瓶修复液|45000|48000||
|182|Japan Foot Smell|脚气霜|30000|33000||
|183|Repairing Paint|驰誉|45000|48000||
|184|LANNA Patch|泰国兰纳足贴|35000|38000||
|185|Skin Eczema Japan|日本皮肤膏|30000|33000||
|186|SADOER Baking Soda|海盐小苏打牙膏|30000|33000||
|187|SAD VC Squalane|维C角鲨烷|15000|18000||
|188|SAD HYDRATE B5|维生素B5|15000|18000||
|189|SAD Collagen Cleanser|胶原洗面奶|40000|43000||
|190|4IN1 Serum SAD|4IN1面部精华液|32000|35000||
|191|AHA BHA SADOER|AHA祛痘精华液|15000|18000||
|192|TERTELL AB Glue|AB胶|35000|38000||
|193|TRT Rendam Kaki|南京同仁堂|32000|35000||
|194|Car Window Lube|车窗润滑剂|45000|48000||
|195|Lemon Fridge Clean|冰箱清洗剂|15000|18000||
|196|Tire Foam|轮胎清洗剂|50000|53000||
|197|Snail Eye Reorganize|蜗牛眼霜|32000|35000||
|198|Korper Form Cleaner|汽车内饰清洗|60000|63000||
|199|EELHOE Eyelash Liquid|黑色睫毛液|32000|35000||
|200|Glass Oil Film|汽车油膜|35000|38000||
|201|NOSE STRIPS|黑头贴|15000|18000||
|202|CARBURETOR CHOKE|化油器清洗剂|60000|63000||
|203|F1 Engine Surface|发动机外部清洗剂|60000|63000||
|204|Dissa Blue Spray|雪松古龙|40000|43000||
|205|Green Air Spray|绿茶清香|40000|43000||
|206|Ultra SP4|SP4牙膏|30000|33000||
|207|Gardenia Hand Cream|栀子花手霜|38000|41000||
|208|Pomegranate Scrub|石榴磨砂膏|35000|38000||
|209|Maycheer Scar|祛疤膏|38000|41000||
|210|Purple Flower|紫花地丁|38000|41000||
|211|FUKANG Skin|肤康抑菌膏|38000|41000||
|212|XBDZ Janpan Scar|杏坂道枝|38000|41000||
|213|Ganoderma Gigi|灵芝牙膏|30000|33000||
|214|SIMISI Soap|艾草皂|15000|18000||
|215|Speed Wing|铸工胶|33000|36000||
|216|PUZHONGDA|普众达|45000|48000||
|217|Car Paint To|划痕液|32000|35000||
|218|MELASMA Relief|黃褐斑霜|34000|37000||
|219|SenAn Carlight|森岸|55000|58000||
|220|Ginseng Serum|人参精华|30000|33000||
|221|HANBOLI|韩泊莉香氛|33000|36000||
|222|Washtank Clean|洗衣槽清洗剂|38000|41000||
|223|XBMK SIYANG|私痒霜|38000|41000||
|224|QIDXIA RUST||60000|63000||
|225|EE Sunflower||37000|40000||
|226|SNOW BLEACH||35000|38000||
|227|LUJIESHI BRAKE||40000|43000||
|228|Tearing Mask||38000|41000||
|229|Exhaust Auto Spray||58000|61000||
|230|DARCI Cockroach||35000|38000||
|231|PAWPAW SCRUB||38000|41000||
|232|SAD Snail Collagen||38000|41000||
|233|BIOAQUA Eyelash||35000|38000||
|234|Insecticide Powder||15000|18000||
|235|DARK SPOT||35000|38000||
|236|PEEL-OFF MASK||30000|33000||
|237|24HR SETTING||35000|38000||
|238|KERMESIC SCAR||35000|38000||
|239|Red40 Hair Serum||50000|53000||
|240|KOJIC FACE WASH||45000|48000||
|241|KOJIC Sunscreen||38000|41000||
|242|Kiss ORANGE||40000|43000||
|243|PAPA Pellet||50000|53000||
|244|Firming DAN||44000|47000||
|245|Pink Japanese Capsule||38000|41000||
|246|HUNMUI Lip||34000|37000||
|247|NUGEN Bloom||45000|48000||
|248|Mullittea 50X SAKURA||15000|18000||
|249|KISS KOJIC Cream||50000|53000||
|250|KISS ROSE SPF||40000|43000||
|251|Omilay SAL ACID||15000|18000||
|252|CJHY Japan Scar||40000|43000||
|253|Azelaic acid 15%||35000|38000||
|254|Omilay01 Retinol||48000|51000||
|255|Omilay02 Hyaluronic||48000|51000||
|256|Omilay03 VC||48000|51000||
|257|Omilay04 RE+NIA||48000|51000||
|258|Omilay05 Collagen||48000|51000||
|259|Omilay06 Bulgarian||48000|51000||
|260|Omilay07 Cocount||48000|51000||
|261|Omilay08 10%Glycolc||48000|51000||
|262|Omilay09 Aloe||48000|51000||
|263|Omilay10 CPEPEY||48000|51000||
|264|DW11=MILK Lotion||48000|51000||
|265|DW12=ALOE VE||48000|51000||
|266|DW13=Snail White||48000|51000||
|267|DW14=Dream Cloud||48000|51000||
|268|DW15=ORANGE KOJIC||48000|51000||
|269|DW16=PAPAYA||48000|51000||
|270|DW17=COCONUT Stra||48000|51000||
|271|DW18=Honey VC||48000|51000||
|272|DW19=Sakura||48000|51000||
|273|DW20=Collagen||48000|51000||
|274|DW21=PINK ADDICT||48000|51000||
|275|OUHOE Whitening Areas||33000|36000||
|276|NETST 5IN1||45000|48000||
|277|Kopi Hitam||35000|38000||
|278|Big L-Karitin||40000|43000||
|279|YUN NAN APDMP||30000|33000||
|280|HK Active Oil||37000|40000||
|281|Smallpox Mark||34000|37000||
|282|100ML GINSENG Light||40000|43000||
|283|3IN1 Hair Dye||60000|63000||
|284|24K GOLDZEN||40000|43000||
|285|West Lip mask||35000|38000||
|286|GUM INSTANT||33000|36000||
|287|Moldable Teeth||32000|35000||
|288|West Hair Spray||33000|36000||
|289|NAVETA COLLAGEN COFFEE||40000|43000||
|290|Der J Orange||34000|37000||
|291|Scrub Kojic Pretty||45000|48000||
|292|LBLS NIA SERUM||50000|53000||
|293|LANYANZHI Snake||32000|35000||
|294|SADOER 90 SPF||38000|41000||
|295|Collagen SPF 50||33000|36000||
|296|SADOER Foot SHEA||30000|33000||
|297|SADOER SNOW||32000|35000||
|298|Honey Peach Cream||40000|43000||
|299|ZOZU 24K Serum||32000|35000||
|300|SADOER Snail Gel||38000|41000||
|301|V34 Toothpaste||38000|41000||
|302|Kojic TONER||50000|53000||
|303|KOJIC EYE CREAM||38000|41000||
|304|SAUSANDO coffee||42000|45000||
|305|CHONGZI Ginger||45000|48000||
|306|EELHOE GINSENG||40000|43000||
|307|Bona Vita|7袋7g|40000|43000||
|308|POUQUR ORANGE|去角质凝胶100g|35000|38000||
|309|Japan Corn Patch|12贴|36000|39000||
|310|Fat Granule Sumifun||33000|36000||
|311|Sum Thai Hemorrhoid||35000|38000||
|312|Bedsore Sumifun||36000|39000||
|313|Ginseng Shampoo||42000|45000||
|314|Aloe Exfoliating Gel||30000|33000||
|315|LAOLISHI Hair Spray||35000|38000||
|316|Man SHK||50000|53000||
|317|Minoxidil Serum||33000|36000||
|318|Cordyceps Glossy||32000|35000||
|319|LBLS SAKURA||15000|18000||
|320|COCO HBL||35000|38000||
|321|SAD Retinol Cleanser||40000|43000||
|322|Bikang ZB||35000|38000||
|323|MEMI SUNBLOCK||40000|43000||
|324|Peach Oral|搭配另外一款。做复合式链接|30000|33000||
|325|V-Vaxy Car||40000|43000||
|326|SeS2 Dandruff||40000|43000||
|327|SP-7 Teeth Powder||33000|36000||
|328|AHA Body Serum||36000|39000||
|329|Jay 7 days||35000|38000||
|330|OUHOE JOINT||35000|38000||
|331|EE Nicotinamide||35000|38000||
|332|OUHOE PURIFYING GEL||35000|38000||
|333|Centella Mask||33000|36000||
|334|Coffee01=10 LUBOV|黑咖啡10袋|35000|38000||
|335|Coffee02=10 ENVE BLACK|黑咖啡10袋|35000|38000||
|336|Coffee03=10 ESPRESSO|黑咖啡10袋|35000|38000||
|337|Coffee04=10 TNI KING|黑咖啡10袋|35000|38000||
|338|Coffee05=10 MOUNT HAGEN|黑咖啡10袋|35000|38000||
|339|Coffee06=10 ENVY WHITE|黑咖啡10袋|35000|38000||
|340|Coffee07=20 AGF|黑咖啡20袋|42000|45000||
|341|Coffee08=20 EDIYA|黑咖啡20袋|42000|45000||
|342|Coffee09=20 Energy|黑咖啡20袋|42000|45000||
|343|Coffee10=20 LANSLEY|黑咖啡20袋|42000|45000||
|344|Coffee11=20 Red LOOKAS9|黑咖啡20袋|42000|45000||
|345|Coffee12=20 X POWER|黑咖啡20袋|42000|45000||
|346|Coffee13=20 CF MACA|黑咖啡20袋|42000|45000||
|347|Coffee14=20 Orange LOOK|黑咖啡20袋|42000|45000||
|348|HR=01EISHOWT||60000|63000||
|349|HR=02MOKERU||60000|63000||
|350|HR=03Black ZWM||60000|63000||
|351|HR=04AUGEAS||60000|63000||
|352|HR=05Kiss Beauty||60000|63000||
|353|HR=06Grey Shampoo||60000|63000||
|354|HR=07CROWNCARE||60000|63000||
|355|EE GINSENG ESSENCE||33000|36000||
|356|Jay ANTI ACNE||33000|36000||
|357|OUH B7 Biotin||35000|38000||
|358|Stop Snoring||35000|38000||
|359|SP14 COORST||30000|33000||
|360|OCHEAL HAIR WAX||35000|38000||
|361|Sausando Collagen||40000|43000||
|362|WLJR GENSENG SQUALANE||40000|43000||
|363|KAIFEIRUI OLAFUR||30000|33000||
|364|Japan Slim Capsule||35000|38000||
|365|HUASURV GOLD||33000|36000||
|366|QISE Ferilla Lotion||35000|38000||
|367|Lutein Drops||30000|33000||
|368|White Flower Oil||35000|38000||
|369|Japan Skin Cream||33000|36000||
|370|MEDICATED OIL||35000|38000||
|371|HCHANA ALOE||30000|33000||
|372|LLS GOLD MASK||32000|35000||
|373|LLS Ginseng Cordyceps||30000|33000||
|374|DRYMR Sulfur Clean||30000|33000||
|375|DRYMR VE Cream||33000|36000||
|376|LLS V7 MASK||33000|36000||
|377|LLS Astaxanthin Cream||33000|36000||
|378|LLS Sulfur Refreshing||43000|46000||
|379|OLIVES OIL||70000|73000||
|380|Shampoo Coconut||55000|58000||
|381|Baby Calendula||38000|41000||
|382|SLIM BODY SAD||33000|36000||
|383|QDQ Collagen||50000|53000||
|384|Astaxanthin Sadoer||42000|45000||
|385|Cucumber Hair Remove||38000|41000||
|386|SADOER Anti-Freckle||30000|33000||
|387|Ringworm Nails Set||50000|53000||
|388|Acupoint Patch||30000|33000||
|389|LBLS Sunscreen Bag||30000|33000||
|390|Aogo GT320S||33000|36000||
|391|Multi-White Toothpaste||45000|48000||
|392|SAD Sleep Spray||38000|41000||
|393|SADOER 377 VC||37000|40000||
|394|Vision Eye||30000|33000||
|395|LANEMAY Scar||36000|39000||
|396|YINBA Lotion||40000|43000||
|397|HK FOOT PASTE||40000|43000||
|398|97.45%Aloe||28000|31000||
|399|HIH FOOT||35000|38000||
|400|VIBEUP Toothache||36000|39000||
|401|HBESTY Slim Patch||35000|38000||
|402|SOL Nails||34000|37000||
|403|SOL Sense Hair||38000|41000||
|404|Men Wash Charcoal||55000|58000||
|405|Kiss VC Peeling||40000|43000||
|406|Kiss Stretch||50000|53000||
|407|SPF UV protection||38000|41000||
|408|AHA 3 DAYS||57000|60000||
|409|Seaweed SAUSANDO||38000|41000||
|410|Scar Sheet01=Sumifun||50000|53000||
|411|Scar Sheet02=ELAIMEI||50000|53000||
|412|Scar Sheet03=EELHOE||42000|45000||
|413|Scar Sheet04=West Month||42000|45000||
|414|Scar Sheet05=Taerikpru||42000|45000||
|415|Scar Sheet06=Vibrum||42000|45000||
|416|Huatuo BFL||30000|33000||
|417|MOIKA Black Serum||32000|35000||
|418|Kreain Joint Gel|100g|50000|53000||
|419|WWP Kojic Cleanser||44000|47000||
|420|Big Belly Patch||32000|35000||
|421|Bamboo Deep Patch||32000|35000||
|422|KangeHB Genital||33000|36000||
|423|SHEEP OIL CREAM||30000|33000||
|424|HYPF APGMA||30000|33000||
|425|SOL FatKare Lip||30000|33000||
|426|AOOFSE 377 NIA||30000|33000||
|427|HK HT Hemorrhoid||33000|36000||
|428|Sum Slim Cream||36000|39000||
|429|FIBSHIELD Car Window||50000|53000||
|430|MELAO Hot Cream||42000|45000||
|431|Car Coat01=iMeiTe|汽车镀膜剂|55000|58000||
|432|Car Coat02=Speed Wax|汽车镀膜剂|55000|58000||
|433|Car Coat03=MikeHam|汽车镀膜剂|55000|58000||
|434|Car Coat04=Japan|汽车镀膜剂|55000|58000||
|435|Car Coat05=Motorcycle|汽车镀膜剂|55000|58000||
|436|Sleep01=NOLL|睡眠贴48pcs|35000|38000||
|437|Sleep02=NERU|睡眠贴48pcs|35000|38000||
|438|Sleep03=UR Clouds|睡眠贴48pcs|35000|38000||
|439|Sleep04=Lucky|睡眠贴48pcs|35000|38000||
|440|Sleep05=U GLOW|睡眠贴48pcs|35000|38000||
|441|Sleep06=Herbal Fit|睡眠贴48pcs|35000|38000||
|442|Sleep07=Corry|睡眠贴48pcs|35000|38000||
|443|Sleep08=LUNA FORE|睡眠贴48pcs|35000|38000||
|444|EELHOE Wart Cream||33000|36000||
|445|Inflammation OUHOE||32000|35000||
|446|OceAura ABS||38000|41000||
|447|Berry Lip Mask||33000|36000||
|448|IEELHOE Lip Cream||33000|36000||
|449|Homonth Tire||33000|36000||
|450|OUHOE Rosemary||36000|39000||
|451|EE Skin Tag||33000|36000||
|452|50g Wart EELHOE||33000|36000||
|453|West AHA BHA||35000|38000||
|454|Camille Sunny|侵权风险|45000|48000||
|455|Dr FAY|侵权风险|42000|45000||
|456|NUOWEIYA Hair||32000|35000||
|457|Sum Earache Drop||35000|38000||
|458|Brown Sampo01=MEIDU||60000|63000||
|459|Brown Sampo02=Kiss Beauty||60000|63000||
|460|Brown Sampo03=CROWNCARE||60000|63000||
|461|Brown Sampo04=MOKERU||60000|63000||
|462|Brown Sampo05=JAPAN||60000|63000||
|463|Brown Sampo06=6IN1||60000|63000||
|464|Brown Sampo07=SADOER||60000|63000||
|465|Brown Sampo08=OUKEYA||60000|63000||
|466|Eye Drop01=Big Eye||35000|38000||
|467|Eye Drop02=Green E40||35000|38000||
|468|Eye Drop03=Black RICH||35000|38000||
|469|Eye Drop04=Blwaho||35000|38000||
|470|Eye Drop05=B6 AE||35000|38000||
|471|Eye Drop06=WHITE BSZY||35000|38000||
|472|500-Sum Foot||34000|37000||
|473|501-Sum Wasir||34000|37000||
|474|502-Lavender Scar||34000|37000||
|475|503-Sum Private||34000|37000||
|476|504-Bunion Pain||34000|37000||
|477|505-Thai Skin Spray||34000|37000||
|478|506-AOFSE Cleanser||34000|37000||
|479|507-ZENSHOW SKIN||32000|35000||
|480|508-ETHEREAL Vitiligo||32000|35000||
|481|509-Tea Tree Ginger|侵权风险|40000|43000||
|482|510-Tummiva Comfort|侵权风险|45000|48000||
|483|511-Kreain Nasal|侵权风险|40000|43000||
|484|512-YuTitan Massage|侵权风险|45000|48000||
|485|513-Krea Skin|侵权风险|40000|43000||
|486|514-Kreain Toothpaste|侵权风险|45000|48000||
|487|515-BUBBLE MASK||34000|37000||
|488|516-Croent Toothpaste||34000|37000||
|489|517-Eye Oil||34000|37000||
|490|518-BS Freckle Cream||35000|38000||
|491|519-Tallow Balm||34000|37000||
|492|520-Magnesium Cream||34000|37000||
|493|521-Bee Venom Wart||34000|37000||
|494|522-Hoygi Exfoliating||34000|37000||
|495|523-Holikea Bee Skin||34000|37000||
|496|524-OUHOE Slimming Oil||34000|37000||
|497|525-Herbal Soothing Cream||34000|37000||
|498|526-Mother Cream||34000|37000||
|499|527-Natural Hair Soap||34000|37000||
|500|528-OUHOE BOTOX BEE||34000|37000||
|501|529-Ximonth Foot Care|足霜。侵权风险|34000|37000||
|502|530-NIPPORI Shampoo|洗发水。侵权风险|45000|48000||
|503|531-SKINVU Lotion|身体乳。侵权风险|55000|58000||
|504|Black Hair Mask01=CONFANY|发膜。侵权风险|43000|46000||
|505|Black Hair Mask02=Keratin|发膜|43000|46000||
|506|Black Hair Mask03=MELAO|发膜|43000|46000||
|507|Black Hair Mask04=SADOER ARGAN|发膜|43000|46000||
|508|WHITE Mask01=JCKOO|发膜。侵权风险|43000|46000||
|509|WHITE Mask02=ELAIMEI|发膜|43000|46000||
|510|WHITE Mask03=KORMESIC NON|发膜|43000|46000||
|511|Corn Patch01=HillGod||40000|43000||
|512|Corn Patch02=NICHIBAN||40000|43000||
|513|Corn Patch03=Scholl||40000|43000||
|514|Corn Patch04=HBESTY|鸡眼贴24片装|38000|41000||
|515|Corn Patch05=ERAYCEE|鸡眼贴24片装|38000|41000||
|516|Corn Patch06=OPPLII|鸡眼贴24片装|38000|41000||
|517|Corn Patch07=Kiss Beauty|鸡眼贴24片装|38000|41000||
|518|Corn Patch08=Sumifun|鸡眼贴24片装|38000|41000||
|519|Corn Patch09=Japan||38000|41000||
|520|Black Hair Mask05=HUNMUI|发膜|43000|46000||
|521|Black Hair Mask06=MEIDU|发膜|43000|46000||
|522|Black Hair Mask07=MELAO|发膜|43000|46000||
|523|Black Hair Mask08=MIEELE|发膜|43000|46000||
|524|Black Hair Mask09=PURE|发膜|43000|46000||
|525|HR=10-DEVNEN Shampoo|黑色一支黑、没有纸盒。侵权|60000|63000||
|526|HR=11-EELHOE Shampoo|黑色一支黑、没有纸盒|60000|63000||
|527|Brown Sampo09=DEVNEN|棕色一支黑。没有纸盒。侵权|60000|63000||
|528|Scar Sheet07=SILICONE|疤痕贴。侵权|45000|48000||
|529|GINSENG Serum03=MOIKA|人参精华液。侵权|40000|43000||
|530|GINSENG Serum04=CONFANY|人参精华液。侵权|40000|43000||
|531|GINSENG Serum05=KORMESIC|人参精华液。侵权|40000|43000||
|532|532-Yutian Skin Cream|皮肤膏20g。侵权风险|48000|51000||
|533|533-Dr Hair Serum|头发生长喷雾30ML。侵权风险|43000|46000||
|534|534-Dr Comfort Massage|舒服按摩膏30g。侵权风险|43000|46000||
|535|535-DrYutian Ear Drop|耳朵滴瓶30ML。侵权风险|43000|46000||
|536|536-Oxyelle Warm Cream|舒缓膏。侵权风险|50000|53000||
|537|537-KN Cooling Gel|痔疮膏。侵权风险|45000|48000||
|538|538-Krean Ear Care|耳朵滴瓶30ML。侵权风险|43000|46000||
|539|539-Krean Leg Cream|腿部霜。侵权风险|40000|43000||
|540|540-SHULUODA PAIN|骨骼霜。侵权风险|40000|43000||
|541|541-HaloseHat Cooling|皮肤按摩膏。侵权风险|55000|58000||
|542|542-Aloe RAYGOLD|头发生长液。侵权风险|55000|58000||
|543|543-Ginseng RAYGOLD|头发生长液。侵权风险|55000|58000||
|544|544-SOLVITA Oil|侵权风险|30000|33000||
|545|545-Greenvibes Body Gel|侵权风险|45000|48000||
|546|546-PHERINI ARMPIT|侵权风险|60000|63000||
|547|547-SKINFLAIR MIKY|侵权风险|60000|63000||
|548|548-Facetology Sunscreen|侵权风险|60000|63000||
|549|549-Mamas Choice|侵权风险|60000|63000||
|550|550-whitelab Cream|侵权风险|50000|53000||
|551|551-Glowby SKIN Serum|侵权风险|60000|63000||
|552|552-Expert Care Cream|侵权风险|70000|73000||
|553|553-ONLYOU Skin Care|侵权风险|50000|53000||
|554|554-LEIKA AHA Serum|侵权风险|50000|53000||
|555|555-Glughava Body Serum|侵权风险|70000|73000||
|556|556-GLOW UP CREAM|侵权风险|45000|48000||
|557|557-SCARLETT AHA Lotion|侵权风险|58000|61000||
|558|558-CLABEAU Lotion|侵权风险|60000|63000||
|559|559-CAZURA Bust|侵权风险|48000|51000||
|560|560-NOROID Intensive|侵权风险|150000|153000||
|561|561-CHALONESE Brightening|侵权风险|45000|48000||
|562|562-V10 WORLAB|侵权风险|120000|123000||
|563|563-Gloow&be Sunscreen|侵权风险|42000|45000||
|564|564-Whitelab Sun Gel|侵权风险|55000|58000||
|565|565-AMURA Spotless|侵权风险|60000|63000||
|566|566-GLOWIES Dreamy|侵权风险|110000|113000||
|567|567-Biotalk Calendula|侵权风险|60000|63000||
|568|568-ELFORMULA CERAHYDRO|侵权风险|80000|83000||
|569|569-Aeekiy Comfort|侵权风险|50000|53000||
|570|570-FILLIZI Massage Gel|侵权风险|55000|58000||
|571|571-Greenvibes Moisturiz|侵权风险|50000|53000||
|572|572-LANZF Massage|侵权风险|40000|43000||
|573|573-Greenvibes Hair|侵权风险|55000|58000||
|574|574-TERATU AHA Lotion|侵权风险(100ML)|70000|73000||
|575|575-Nubiko Baby Cream|侵权风险|60000|63000||
|576|576-0% Hair Color|侵权风险|60000|63000||
|577|577-MEETFACE Golden|侵权风险|40000|43000||
|578|578-FILLIZI NASAL|侵权风险|50000|53000||
|579|579-Kids Der Ultra|侵权风险|95000|98000||
|580|580-NEARFOREST Savior|侵权风险|90000|93000||
|581|581-Aavini Comfort|侵权风险|40000|43000||
|582|582-Oxyelle Women Wash|侵权风险|55000|58000||
|583|583-HEYXI Retinol|侵权风险|35000|38000||
|584|584-Beautyhack FLO|侵权风险|70000|73000||
|585|585-Amaterasun Physical|侵权风险|40000|43000||
|586|586-Essential Soothe|侵权风险|55000|58000||
|587|587-Hansaplast Salep|侵权风险|45000|48000||
|588|Carlight Spray02=TUBEER|汽车大灯清洗剂|45000|48000|新品到货可卖|
|589|Carlight Spray03=Red XML|汽车大灯清洗剂|45000|48000|新品到货可卖|
|590|Carlight Spray04=Kineshinex|汽车大灯清洗剂|45000|48000|新品到货可卖|
|591|Carlight Spray05=Fantastic|汽车大灯清洗剂|45000|48000|新品到货可卖|
|592|588-AHE HAIRFALL|仿品洗发水|50000|53000|新品到货可卖|
|593|589-PNEUMA GINSENG|仿品洗发水|50000|53000|新品到货可卖|
|594|590-OENAYIM Sampo|普货-洗发水|47000|50000|新品到货可卖|
|595|591-Olive Oil|普货-橄榄油|37000|40000|新品到货可卖|
|596|592-Herbikids Baby|仿品|62000|65000|新品到货可卖|
|597|593-SOMBONG BARRIER|仿品|42000|45000|新品到货可卖|
|598|594-Transpulmin Baby|仿品|67000|70000|新品到货可卖|
|599|595-Black SOMBONG|仿品|42000|45000|新品到货可卖|
|600|596-Yellow FUYANG Cream|普货-皮肤膏|37000|40000|新品到货可卖|
|601|597-SCULPT Underarm|仿品|62000|65000|新品到货可卖|
|602|598-Niacef Gel|仿品|37000|40000|新品到货可卖|
|603|599-Ehmznv Hair Wand|普货|37000|40000|新品到货可卖|
|604|600-GMH Mith Wash|普货|52000|55000|新品到货可卖|
|605|601-Glowby Kids Daily|仿品|57000|60000|新品到货可卖|
|606|602-Amaterasun UV Serum|仿品|42000|45000|新品到货可卖|
|607|603-White Inc AHA|仿品|42000|45000|新品到货可卖|
|608|604-Eye Strips|仿品|52000|55000|新品到货可卖|
|609|605-Rtop Ginger Nail|仿品|37000|40000|新品到货可卖|
|610|606-SOL Wart Remover|普货|32000|35000|新品到货可卖|
|611|607-APIAP Skin Care|普货|32000|35000|新品到货可卖|
|612|608-HK Scar Cream|普货|32000|35000|新品到货可卖|
|613|609-Japan Wart|普货|32000|35000|新品到货可卖|
|614|610-Glucosamine Massage|普货|32000|35000|新品到货可卖|
|615|611-Herbal YNBC Wart|普货|32000|35000|新品到货可卖|
|616|612-Nail Repair Japan|普货|32000|35000|新品到货可卖|
|617|613-SCALP CLEANSING|普货|35000|38000|新品到货可卖|
|618|614-Tiroid Krim|普货|35000|38000|新品到货可卖|
|619|615-Mamas Daily Face|仿品|92000|95000|新品到货可卖|
|620|616-PINKFUTURE Ginseng|仿品|42000|45000|新品到货可卖|
|621|617-ACNAWAY ACNE|仿品|42000|45000|新品到货可卖|
|622|618-Vortextract Tea|普货-自己品牌|52000|55000|未到货|
|623|619-BaiYaoLang Herbal|普货-皮肤膏|42000|45000|新品到货可卖|
|624|620-Bonvie GIN|仿品|56000|59000|新品到货可卖|
|625|621-B5 10% Minimalist|仿品|66000|69000|新品到货可卖|
|626|622-GLOWING UNDERARM|仿品|61000|64000|新品到货可卖|
|627|623-Bepanthen Baby|仿品|51000|54000|新品到货可卖|
|628|624-NPURE CICA SUN|仿品|64000|67000|新品到货可卖|
|629|625-RETINOL 5X FIRMING|爆款。品牌被包销。不要上虾皮猫店|51000||新品到货可卖|
|630|626-Expce Herbal Tea|仿品|49000||新品到货可卖|
|631|627-Acne Spot Skinflair|仿品-爆款|64000||新品到货可卖|
|632|628-YONGLOW RETINOL|仿品|39000||新品到货可卖|
|633|629-Rintik Bump|仿品|72000||新品到货可卖|
|634|630-Parasol Sunscreen|仿品|54000||新品到货可卖|
|635|631-THROMBOPHOB Gel|仿品|57000||新品到货可卖|
|636|632-INTOFACE Acne|仿品|52000||新品到货可卖|
|637|633-Noda Hitam|仿品|38000||新品到货可卖|
|638|634-Buttered Almond|仿品120ML|80000||新品到货可卖|
|639|635-Velltrua Spot|仿品|45000||新品到货可卖|
|640|636-XP Niaclear|仿品|37000||新品到货可卖|
|641|637-DER ACNE SPOT|仿品|110000||新品到货可卖|
|642|Acne Wart01=EELHOE|144贴-可上猫店|35000|38000|新品到货可卖|
|643|Acne Wart02=SKIN TAG|144贴-可上猫店|35000|38000|新品到货可卖|
|644|Acne Wart03=Royal Prestige|144贴-可上猫店|35000|38000|新品到货可卖|
|645|Acne Wart04=Sumifun Tag|144贴-可上猫店|35000|38000|新品到货可卖|
|646|Acne Wart05=JAYSUING SKIN|144贴-可上猫店|35000|38000|新品到货可卖|
|647|Acne Wart06=OUHOE DARTS|144贴-可上猫店|35000|38000|新品到货可卖|
|648|Acne Wart07=ELAIMEI SKIN|144贴-不建议上猫店|39000|42000|新品到货可卖|
|649|Acne Wart08=SEFUDUN SKIN|144贴-不建议上猫店|39000|42000|新品到货可卖|
|650|Acne Wart09=HITWORKER|144贴-可上猫店|39000|42000|新品到货可卖|
|651|Acne Wart10=ELAIMEI ACNE|144贴-不建议上猫店|39000|42000|新品到货可卖|
|652|Temp Teeth01=SEFUDUN|30g-1688品|39000|42000|新品到货可卖|
|653|Temp Teeth02=ROYAL|30g-1688品|39000|42000|新品到货可卖|
|654|Temp Teeth03=FAY KIT|30g-自有品牌|39000|42000|新品到货可卖|
|655|Temp Teeth04=Omilay Minute|30g-自有品牌|39000|42000|新品到货可卖|
|656|Temp Teeth05=GLAD KIT|30g-自有品牌|39000|42000|新品到货可卖|
|657|Temp Teeth06=Green Omilay|30g-自有品牌|39000|42000|新品到货可卖|
|658|Temp Teeth07=GLAD Maximum|30g-自有品牌|39000|42000|新品到货可卖|
|659|Temp Teeth08=FAYKISS Mins|30g-自有品牌|39000|42000|新品到货可卖|
|660|Temp Teeth09=GLAD CODE|30g-自有品牌|39000|42000|新品到货可卖|
|661|Temp Teeth10=Foreign Men|30g-自有品牌|39000|42000|新品到货可卖|
|662|Face LIFT01=Pink FAY|100片-自有品牌|39000|42000|新品到货可卖|
|663|Face LIFT02=GLAD CODE|100片-自有品牌|39000|42000|新品到货可卖|
|664|Face LIFT03=Omilay|100片-自有品牌|39000|42000|新品到货可卖|
|665|Face LIFT04=Purple Omilay|100片-自有品牌|39000|42000|新品到货可卖|
|666|Face LIFT05=GLAD LINE|100片-自有品牌|39000|42000|新品到货可卖|
|667|Face LIFT06=FAYKISS|100片-自有品牌|39000|42000|新品到货可卖|
|668|Face LIFT07=Brown iBea|100片-1688品|39000|42000|新品到货可卖|
|669|Face LIFT08=Blue iBealee|100片-1688品|39000|42000|新品到货可卖|
|670|Face LIFT09=Purple iBea|100片-1688品|39000|42000|新品到货可卖|
|671|Scar Sheet08=Fay Muscles|疤痕贴|50000|53000|新品到货可卖|
|672|Scar Sheet09=Glad Code|疤痕贴|50000|53000|新品到货可卖|
|673|Scar Sheet10=NewGel|疤痕贴|50000|53000|新品到货可卖|
|674|Scar Sheet11=MyHelp|疤痕贴|50000|53000|新品到货可卖|
|675|Scar Sheet12=FAYKISS TAPE|疤痕贴|50000|53000|新品到货可卖|
|676|638-Kutil Tahlalat|祛疣精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|677|639-Omilay Wart Callus|祛疣精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|678|640-Glad TARGETS Wart|祛疣精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|679|641-Glad Blue Wart|祛疣精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|680|642-FAYKISS Liquld Wart|祛疣精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|681|643-FAY Remover Cream|祛疣膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|682|644-BEE VENOM Wart|祛疣膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|683|645-SKIN TAG REMOVER|祛疣膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|684|646-Glad Wart Cream|祛疣膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|685|647-Omilay WART&CORN|祛疣膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|686|648-Black Wart Pen|祛疣笔-自有品牌可上猫店|40000|43000|新品到货可卖|
|687|649-SKIN TAG PEN|祛疣笔-自有品牌可上猫店|40000|43000|新品到货可卖|
|688|650-Green Wart Pen|祛疣笔-自有品牌可上猫店|40000|43000|新品到货可卖|
|689|651-Red Wart Pen|祛疣笔-自有品牌可上猫店|40000|43000|新品到货可卖|
|690|652-Omilay Wart Pen|祛疣笔-自有品牌可上猫店|40000|43000|新品到货可卖|
|691|653-Days Nail FUNGUS|指甲精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|692|654-Glad NAIL RENEWAL|指甲精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|693|655-MultiPurpose Nail|指甲精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|694|656-GREY NAIL CARE|指甲精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|695|657-TOENAIL FUNGUS|指甲精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|696|658-Omilay Seawater Nasal|鼻喷-自有品牌可上猫店|40000|43000|新品到货可卖|
|697|659-MultiSymptom Nasal|鼻喷-自有品牌可上猫店|40000|43000|新品到货可卖|
|698|660-Aloe Saline Nasal|鼻喷-自有品牌可上猫店|40000|43000|新品到货可卖|
|699|661-Oxymetazoline Nasal|鼻喷-自有品牌可上猫店|40000|43000|新品到货可卖|
|700|662-Cold Nasal Spray|鼻喷-自有品牌可上猫店|40000|43000|新品到货可卖|
|701|663-Fay Tinnitus Spray|耳鸣喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|702|664-Glad Tinnitus Spray|耳鸣喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|703|665-Faykiss Blue Spray|耳鸣喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|704|666-Omilay Purple Tinnitus|耳鸣喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|705|667-Red Tinnitus Spray|耳鸣喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|706|668-Days King Ginger|头发生长喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|707|669-Pink Hair Spray|头发生长喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|708|670-3in1 Hair Spray|头发生长喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|709|671-Black Rice Hair|头发生长喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|710|672-Minoxidil B7 Hair|头发生长喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|711|673-Omilay King Ginger|头发精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|712|674-FAY ROSEMARY OIL|头发精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|713|675-Glad hair OIL|头发精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|714|676-FAYKISS 5% MINOXIDIL|头发精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|715|677-Glad HAIR SERUM|头发精华液-自有品牌可上猫店|40000|43000|新品到货可卖|
|716|678-5% BEARD OIL|胡子油-自有品牌可上猫店|40000|43000|新品到货可卖|
|717|679-Glad BEARD OIL|胡子油-自有品牌可上猫店|40000|43000|新品到货可卖|
|718|680-PURE ORGANIC OIL|胡子油-自有品牌可上猫店|40000|43000|新品到货可卖|
|719|681-CLASSIC BEARD OIL|胡子油-自有品牌可上猫店|40000|43000|新品到货可卖|
|720|682-Omilay BEARD OIL|胡子油-自有品牌可上猫店|40000|43000|新品到货可卖|
|721|683-Omilay LIPOMA|脂肪瘤膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|722|684-FAYKISS Lipoma|脂肪瘤膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|723|685-FAY Lipoma Cream|脂肪瘤膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|724|686-GLAD Lipoma Cream|脂肪瘤膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|725|687-Glad Purple Lipoma|脂肪瘤膏-自有品牌可上猫店|40000|43000|新品到货可卖|
|726|688-Omilay Instant Spray|牙痛灵喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|727|689-GLAD Toothache Spray|牙痛灵喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|728|690-FAY Toothache Spray|牙痛灵喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|729|691-FAYKISS Relief Spray|牙痛灵喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|730|692-GLAD Instant Tooth|牙痛灵喷雾-自有品牌可上猫店|40000|43000|新品到货可卖|
|731|693-GLAD Cooling Eye|眼药水-自有品牌可上猫店|40000|43000|新品到货可卖|
|732|694-Heavenly Bright|眼药水-自有品牌可上猫店|40000|43000|新品到货可卖|
|733|695-Cooling Eye Drops|眼药水-自有品牌可上猫店|40000|43000|新品到货可卖|
|734|696-FAY Bright Eyes|眼药水-自有品牌可上猫店|40000|43000|新品到货可卖|
|735|697-Dry Eye Therapy|眼药水-自有品牌可上猫店|40000|43000|新品到货可卖|
|736|FOOT PADS01=Herbal|足贴30片，可上猫店|42000|45000|新品到货可卖|
|737|FOOT PADS02=Fay Bamboo|足贴30片，可上猫店|42000|45000|新品到货可卖|
|738|FOOT PADS03=2in1 Ginger|足贴30片，可上猫店|42000|45000|新品到货可卖|
|739|FOOT PADS04=Natural Bamboo|足贴30片，可上猫店|42000|45000|新品到货可卖|
|740|FOOT PADS05=OverNight|足贴30片，可上猫店|42000|45000|新品到货可卖|
|741|FOOT PADS06=Faykiss Natural|足贴30片，可上猫店|42000|45000|新品到货可卖|
|742|FOOT PADS07=BEE VENOM|足贴30片，可上猫店|42000|45000|新品到货可卖|
|743|FOOT PADS08=SEFUDUN Bamboo|足贴30片，可上猫店|42000|45000|新品到货可卖|
|744|FOOT PADS09=Purple Relax|足贴30片，可上猫店|42000|45000|新品到货可卖|
|745|FOOT PADS10=Deep Clean|足贴30片，可上猫店|42000|45000|新品到货可卖|
|746|698-L-Ascorbic Acid|仿品|80000||新品到货可卖|
|747|699-SOL Psoriasis|普货-可上猫店|35000|38000|新品到货可卖|
|748|700-CHEILITIS CREAM|普货-可上猫店|35000|38000|新品到货可卖|
|749|701-LUMBAR PAIN|普货-可上猫店|35000|38000|新品到货可卖|
|750|702-Scar Diminish|普货-可上猫店|35000|38000|新品到货可卖|
|751|703-Athlete Foot|普货-可上猫店|35000|38000|新品到货可卖|
|752|704-Scar Japan Gel|普货-可上猫店|35000|38000|新品到货可卖|
|753|705-Japan Sooth Massage|普货-可上猫店|35000|38000|新品到货可卖|
|754|706-Teosheli Nia Acid|普货-可上猫店|35000|38000|新品到货可卖|
|755|707-Wig Detangle Spray|普货-可上猫店|35000|38000|新品到货可卖|
|756|708-Yellow Mole Cream|普货-可上猫店|35000|38000|新品到货可卖|
|757|709-Herb Corn|普货-可上猫店|35000|38000|新品到货可卖|
|758|710-Bone Penetrat|普货-可上猫店|35000|38000|新品到货可卖|
|759|711-KILLMISE QUICK|普货-可上猫店|35000|38000|新品到货可卖|
|760|Women Cap01=Japan Gel|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|761|Women Cap02=Glad NAGINAL|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|762|Women Cap03=Puple Princess|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|763|Women Cap04=Moisturizing|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|764|Women Cap05=DUFT-NETST|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|765|Women Cap06=Green PAPA|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|766|Women Cap07=GIRL DAN|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|767|Women Cap08=FAY Vaginal|紧润丸-敏感但不是仿品|52000|55000|新品到货可卖|
|768|712-Red Counterpain|关节膏。仿品|70000||新品到货可卖|
|769|HAIR COMB01=BLACK FAY|可上猫店|55000|58000|新品到货可卖|
|770|HAIR COMB 02=LICHEN|可上猫店|55000|58000|新品到货可卖|
|771|HAIR COMB03=3X FAYKISS|自有品牌。但是外观仿不上猫店|55000|58000|新品到货可卖|
|772|HAIR COMB04=Herbal Glad|自有品牌。但是外观仿不上猫店|55000|58000|新品到货可卖|
|773|HAIR COMB05=SOL LORA|可上猫店|55000|58000|新品到货可卖|
|774|HAIR COMB06=FAYKISS 300ML|可上猫店|55000|58000|新品到货可卖|
|775|HAIR COMB07=3IN1 CPIC|可上猫店|55000|58000|新品到货可卖|
|776|HAIR COMB08=KEMIRI HAIR|自有品牌。但是外观仿不上猫店|55000|58000|新品到货可卖|
|777|HAIR COMB09=APPLE GLAD|可上猫店|55000|58000|新品到货可卖|
|778|713-HK Nail Repair|普货-可上猫店|30000||本期新品到货可上架|
|779|714-DRREROIA HAIR|自有品牌。但是外观仿不上猫店|35000||本期新品到货可上架|
|780|715-EZROLII CKEAR GEL|普货-可上猫店|33000||本期新品到货可上架|
|781|716-CYPRESS LEAF SOAP|普货-可上猫店|30000||本期新品到货可上架|
|782|717-Collagen Foot SADOER|普货-可上猫店|30000||本期新品到货可上架|
|783|718-CLEANSER KOJIC KOR|普货-可上猫店|30000||本期新品到货可上架|
|784|719-Picdo Tag Eraser|普货-可上猫店|38000||本期新品到货可上架|
|785|720-HNH Acne Spot|仿品|40000||本期新品到货可上架|
|786|721-SYMWHITE TONER|仿品|50000||本期新品到货可上架|
|787|722-Elzet FLEK Night|仿品|38000||本期新品到货可上架|
|788|723-Ciara Stretch|仿品|53000||本期新品到货可上架|
|789|724-Baltikh Underarm|仿品|65000||本期新品到货可上架|
|790|725-COOL Analgesic|仿品|80000||本期新品到货可上架|
|791|726-RUDY M4X HAIR|仿品|60000||本期新品到货可上架|
|792|727-AXISY Dark Spot|仿品-50ML|100000||本期新品到货可上架|
|793|728-ERHA Sunscreen|仿品|70000||本期新品到货可上架|
|794|729-SHENOX FLEK|仿品-20g|50000||本期新品到货可上架|
|795|730-Voltaren Emulgel|仿品-50g|90000||本期新品到货可上架|
|796|731-Glowing Booster|仿品|50000||本期新品到货可上架|
|797|732-ADARA BEE GEL|仿品|45000||本期新品到货可上架|
|798|733-Brightsip Tooth|仿品|45000||在途新品|
|799|734-NOERA ALPHA|仿品|150000||在途新品|
|800|735-AR Raihan|仿品|60000||在途新品|
|801|736-Wish BoykeCo|仿品|100000||在途新品|
|802|737-Bamboo Faykiss|自有品牌。但是外观仿不上猫店|35000||在途新品|
|803|738-Healthier Teeth|普货-可上猫店|35000||在途新品|
|804|739-ETHEREAL LIPOMA|普货-可上猫店|32000||在途新品|
|805|740-CIARA Chamomile|仿品|60000||在途新品|
|806|741-LION PAIR|仿品-24g|100000||在途新品|
|807|742-Loluna 5X Baby|仿品|80000||在途新品|
|808|743-Hand 8X Cream|普货-可上猫店|30000||在途新品|
|809|744-Scar KORMESIC Gel|普货-可上猫店|30000||在途新品|
|810|745-Nourishing Acne Gel|普货-可上猫店|30000||在途新品|
|811|746-KOJIC Facial Cleanser|普货-可上猫店|32000||在途新品|
|812|747-Collagen Pell Off|普货-可上猫店|35000||在途新品|
|813|748-Black AHA Cleanser|普货-可上猫店|32000||在途新品|
|814|749-Japan Herbal Gel|普货-可上猫店|32000||在途新品|
|815|750-Dolphin Baby Sun|普货-可上猫店|40000||在途新品|
|816|751-Warming Sooth Japan|普货-可上猫店|32000||在途新品|
|817|752-Kormesic V34 Tooth|普货-可上猫店|35000||在途新品|
|818|753-Matte Pink Spray|普货-可上猫店|35000||在途新品|
|819|754-Light Green Spray|普货-可上猫店|35000||在途新品|
|820|755-Elephant Baby Soothing|普货-可上猫店|32000||在途新品|
|821|756-Kids Gentle Lotion|普货-可上猫店|35000||在途新品|
|822|757-Kormesic Pain Relief|普货-可上猫店|35000||在途新品|
|823|758-Calamine Kids Cream|普货-可上猫店|32000||在途新品|
|824|759-Milk Oat Kids|普货-可上猫店|32000||在途新品|
|825|760-Kojic Peel-off Mask|普货-可上猫店|35000||在途新品|
|826|761-Kojic Underarm Glow|普货-可上猫店|32000||在途新品|
|827|762-Private Man Cream|普货-可上猫店|30000||在途新品|
|828|763-Women Private Pink|普货-可上猫店|30000||在途新品|
|829|764-377 White Cleanser|普货-可上猫店|32000||在途新品|
|830|765-Fresh Tinted Sun|普货-可上猫店|32000||在途新品|
|831|766-WHITE Anti-Freckle|普货-可上猫店|32000||在途新品|
|832|767-Papaya Scrub|普货-可上猫店|32000||在途新品|
|833|768-SCAR 2% DIMETHICONE|普货-可上猫店|32000||在途新品|
|834|769-Firm 4D Serum|普货-可上猫店|32000||在途新品|
|835|770-Glutathione Underarm|普货-可上猫店|35000||在途新品|
|836|771-20% Azelaic Acid|普货-可上猫店|32000||在途新品|
|837|772-Glowing Nia Gel|普货-可上猫店|32000||在途新品|
|838|773-Repairing 10X Hand|普货-可上猫店|32000||在途新品|
|839|774-MEN MITE Cleanser|普货-可上猫店|38000||在途新品|
|840|775-Massage Gel Repair|普货-可上猫店|35000||在途新品|
|841|776-Daily Tone Up|普货-可上猫店|32000||在途新品|
|842|777-Kormesic Acne Cream|普货-可上猫店|32000||在途新品|
|843|778-Dark Sport Kormesic|普货-可上猫店|32000||在途新品|
|844|779-Ginseng Coffee Cleanser|普货-可上猫店|35000||在途新品|
|845|780-Kormesic Lipoma Gentle|普货-可上猫店|32000||在途新品|
|846|781-RETINOL ANTI-AGING|普货-可上猫店|32000||在途新品|
|847|782-NECK THROAT|自有品牌。但是外观仿不上猫店|32000||在途新品|
|848|783-MEJISOO SILKY|普货-可上猫店|35000||在途新品|
|849|784-ROSIN EYELASH|普货-可上猫店|32000||在途新品|
|850|785-Yellow Astragalus|普货-可上猫店|32000||在途新品|
|851|786-Kids UVA Sunscreen|普货-可上猫店|32000||在途新品|
|852|787-Collagen Hand SDA|普货-可上猫店|32000||在途新品|
|853|788-Baby Lip Balm|普货-可上猫店|32000||在途新品|
|854|789-BAISHU Dewdrop Water|普货-可上猫店|32000||在途新品|
|855|790-Collagen Lip Sadoer|普货-可上猫店|32000||在途新品|
|856|791-Coconut Hand Oil|普货-可上猫店|32000||在途新品|
|857|792-CWINTER Sea Salt|普货-可上猫店|32000||在途新品|
|858|793-OATS AMINO ACID|普货-可上猫店|32000||在途新品|
|859|794-NUBIKO BABY FACE|仿品|55000||在途新品|
|860|795-NPURE Noni Cleanser|仿品|50000||在途新品|
|861|796-FAMEIRA Slim Gel|仿品|60000||在途新品|
|862|797-Orange Eyelash Glue|普货-可上猫店|32000||在途新品|
|863|798-YAPING ICE Sun|普货-可上猫店|32000||在途新品|
|864|799-SOL Varicose Vein|普货-可上猫店|32000||在途新品|
|865|800-Gentle Cooling Gel|普货-可上猫店|32000||在途新品|
|866|801-Tiger Psoriasis|普货-可上猫店|30000||在途新品|
|867|802-Kpemot Femoppor|普货-可上猫店|32000||在途新品|
|868|803-LORA ABC Infection|普货-可上猫店|32000||在途新品|
|869|804-Retinol HA Collagen|普货-可上猫店|32000||在途新品|
|870|805-HERBAL PLANT ACNE|普货-可上猫店|30000||在途新品|
|871|806-LICORICE NPURE|仿品|50000||在途新品|
|872|807-WHITE VC CHALONESE|仿品|50000||在途新品|
|873|808-Ultra Baby SPF50|自有品牌。但是外观仿不上猫店|40000||在途新品|
|887|Body Patch01=BURN-FAT|作废|=DISPIMG("ID_E4B94FA169B34FD7BE5FF6B23610C03C",1)|||
|888|Body Patch02=Capsicum|作废|=DISPIMG("ID_682BC31284E44CD49D467E566B7D651D",1)|||
|889|Body Patch03=Pain Relief|作废|=DISPIMG("ID_AC083787B9E0424ABC52036589D5A3D2",1)|||
|890|Body Patch04=LIPOMA|作废|=DISPIMG("ID_288A260470784662BB1F9F0FF827A6E8",1)|||
|891|Body Patch05=ERAYCEE|作废|=DISPIMG("ID_E1FCB4B51EF74E3EAE95BF6A67420278",1)|||
|892|Body Patch06=JAPAN PAIN|作废|=DISPIMG("ID_F2E887ADC59D4AC58CA63124F8280AA4",1)|||
|893|Body Patch07=Sum Lipoma|作废|=DISPIMG("ID_45F6245037134F75BE798B153C22508B",1)|||
|894|Body Patch08=Gout Sum|作废|=DISPIMG("ID_5615030CE8604BD3A2EDDEED6E669B34",1)|||
|895|Body Patch09=HEEL PAIN|作废|=DISPIMG("ID_C803538954F149188243A1D98F9A9148",1)|||
|896|Body Patch10=SCIATIC NERVE|作废|=DISPIMG("ID_9A3C6BDF52184A78BC61AA97D8AB42C6",1)|||
|897|Body Patch11=Joint Relief|作废|=DISPIMG("ID_73C6836AB5CF486282407EA7F64F058F",1)|||
|898|Body Patch12=MiaoFang|作废|=DISPIMG("ID_B54E4C4279524874B194A2B0002E01EC",1)|||
|899|Body Patch13=Varicose Veins|作废|=DISPIMG("ID_C0AA8461ABAC4A5FBEFDAF4295A868BB",1)|||
|900|Kill Rodent01=MoonSpry|作废|=DISPIMG("ID_0707BFD8E5C9407AB3E4B8E4D7A13EF3",1)|||
|901|Kill Rodent02=FASTBOAT|作废|=DISPIMG("ID_C05CE5602A4E43A5A7922B4EC559F0E8",1)|||
|902|Kill Rodent03=KEEP MICE|作废|=DISPIMG("ID_770406CAB9D5437F9E94AF49D4EB86A0",1)|||
