# Ch4 嫁接 INSERTION 数据
INSERTIONS = [
    # 1 · ATP plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"lead\">骨骼肌中所有的机械功——肌动蛋白 (actin) 沿肌球蛋白 (myosin) 滑动产生的力——只接受一种支付方式:ATP 水解为 ADP + Pi,释放约 30.5 kJ/mol 的吉布斯自由能。无论你是在跑 100m 还是 100K,无论你是慢肌还是快肌,从骨架到分子层级,这套支付协议从未改变。</p>",
        "insert": """  <p class="plain">原理:ATP 水解为 ADP + Pi 释放 30.5 kJ/mol 能量。<strong>翻译:</strong>ATP(三磷酸腺苷)是肌肉唯一收的"现金",一花就拆成 ADP + 磷酸。<em>放在跑步场景:</em>你身上的 ATP 现金存款只够 3 秒钟全力,所以"花掉就立刻印新的"——三大供能系统就是 3 台印钞机。</p>""",
    },
    # 2 · PCr plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>这是一个<strong>非氧化、非糖酵解</strong>的快速重合成通路。没有副产物(除了 H⁺ 短暂消耗,反而起缓冲作用),最大功率高达 9 mmol ATP/kg/s——是三系统中爆发力最强者。但因为 PCr 储量有限,最大功率只能维持 <em>6–8 秒</em>,之后 PCr 浓度降至基线的 30% 以下,系统输出迅速衰减。</p>",
        "insert": """  <p class="plain">原理:PCr(磷酸肌酸)+ ADP → ATP,功率 9 mmol/kg/s,维持 6–8 秒。<strong>翻译:</strong>PCr 是肌肉自带的"应急充电宝",一插就给 ATP 满血续上,容量小、转速快。<em>放在跑步场景:</em>起跑前 50 米、最后冲线 100 米、坡道冲顶——靠的就是它;6–8 秒后这块电池就空了,接力交给糖酵解。</p>""",
    },
    # 3 · 糖酵解 plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>葡萄糖(来自肌糖原或血糖)经 10 步酶促反应分解为 <em>丙酮酸</em>(pyruvate),净产 2 mol ATP/葡萄糖。这一过程发生在<strong>细胞质</strong>,不需要氧气。最大功率约 4–5 mmol ATP/kg/s,低于磷酸原但高于有氧氧化,可持续约 2 分钟达到全力。</p>",
        "insert": """  <p class="plain">原理:糖酵解 = 葡萄糖经 10 步酶反应 → 丙酮酸,净产 2 个 ATP,不需要氧。<strong>翻译:</strong>糖酵解像"小推车搬钱"——速度快但每趟只搬 2 块;同样一个葡萄糖,有氧能搬 30 块。<em>放在跑步场景:</em>400-800m 全力跑、5K 最后 1 km 冲刺——腿酸、心率飙的那种状态,就是糖酵解被推到顶。</p>""",
    },
    # 4 · LT1/LT2/MLSS plain (consolidated)
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>所以现代生理学家更愿意叫它<em>乳酸阈 lactate threshold</em>而不是\"乳酸堆积阈\"——这条线标记的不是\"乳酸开始产生\"的速度,而是\"乳酸产生速率开始超过清除速率\"的临界点。在此之下,血乳酸保持稳态(约 1–2 mmol/L);在此之上,血乳酸持续上升,标志着糖酵解贡献超过了线粒体氧化的处理能力。</p>",
        "insert": """  <p class="plain">原理:LT1(约 2 mmol/L)= 乳酸首次脱离基线的强度;LT2(约 4 mmol/L)= 乳酸产生速率超过清除的临界配速,即 MLSS 最大乳酸稳态。<strong>翻译:</strong>LT1 是水龙头开始滴水;LT2 是水龙头比排水管快,浴缸开始蓄水。<em>放在跑步场景:</em>LT1 ≈ 能边跑边讲完整句话的最快速度(Z2 上限);LT2 ≈ 半马配速 / 10K 配速慢 10-15 秒,只能讲短句、1 小时全力上限。它比 VO2max 更精准决定马拉松成绩。</p>""",
    },
    # 5 · Crossover plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"lead\">George Brooks 在 1994 年提出 crossover concept(交叉点概念):在静息和低强度下,脂肪是主要燃料;随着强度上升,糖类的相对贡献持续上升,直到在某个强度点上糖类供能超过脂肪——这就是 crossover point。这是耐力运动生理学最优雅的一张曲线。</p>",
        "insert": """  <p class="plain">原理:Crossover Concept = 强度上升时脂肪/糖类供能比例反转的那一点,约在 50% VO2max。<strong>翻译:</strong>身体烧两种燃料:脂肪(便宜、量大、烧得慢)和糖(贵、量小、烧得快)。强度低用脂肪,强度高切换到糖,过渡点叫 crossover。<em>放在跑步场景:</em>Z2 配速(能完整对话)主要烧脂肪;到了 Tempo 配速(只能蹦短句),油门已经全切到糖了。</p>""",
    },
    # 6 · VO2max plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"lead\">最大摄氧量 VO2max(maximal oxygen uptake)是描述有氧能力的\"金标准\",定义为递增负荷运动中肌肉每分钟每公斤体重能消耗的最大氧气量,单位 <em>ml/kg/min</em>。它是耐力表现的三大支柱之一,虽然不是唯一决定因素,但它划定了天花板的高度。</p>",
        "insert": """  <p class="plain">原理:VO2max = 每分钟每公斤体重能消耗的最大氧气量(ml/kg/min)。<strong>翻译:</strong>它是你的"发动机最大排量"——一分钟最多能吸进多少氧并送到肌肉烧。<em>放在跑步场景:</em>业余跑者 50,精英 80,Kipchoge 估 84。VO2max 划定了你 5K 的成绩天花板,但马拉松成绩还要看你能维持多高的"百分比"(LT2)和经济性(RE)。</p>""",
    },
    # 7 · Fick 方程 plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>VO2 = Q × (a-vO2 diff) = SV × HR × (a-vO2 diff),其中:</p>",
        "insert": """  <p class="plain">原理:Fick 方程 VO2 = Q × (a-vO2 diff) = SV × HR × (a-vO2 diff)。<strong>翻译:</strong>身体一分钟用多少氧 = 心脏一分钟泵多少血(Q) × 每升血肌肉能扒走多少氧。Q 又拆成"每次跳泵多少血"(SV) × "每分钟跳多少下"(HR)。<em>放在跑步场景:</em>HIIT 把 SV 撑大(心房像气球),Z2 跑把"扒氧能力"撑大(线粒体 + 毛细血管)。两种练法各管一半,缺一不可。</p>""",
    },
    # 8 · RE plain
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"lead\">两位 VO2max 都是 70 的跑者,马拉松成绩可能差 10 分钟,差别在哪?在 <em>跑步经济性</em>(running economy, RE)——同样配速下消耗多少氧。RE 越低 = 越省油 = 同样 VO2max 能跑出更快的速度。</p>",
        "insert": """  <p class="plain">原理:RE(Running Economy)= 每公里每公斤体重消耗的氧(ml/kg/km),越低越省。<strong>翻译:</strong>RE 是发动机的"油耗"——同样的发动机大小(VO2max),油耗越低跑得越远。<em>放在跑步场景:</em>业余 240、精英 180、Kipchoge 估 190。VO2max 5 年就摸到天花板,但 RE 可以连续改善 10 年——这就是"老跑者越跑越省"的秘密,主力训练是力量 + 跑姿 + 肌腱弹性。</p>""",
    },
    # 9 · VO2max ops + you 组合
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>VO2max 是\"上限\",训练能提升 10–25%,但很难超过遗传天花板。HERITAGE Family Study(20 周标准训练)发现 VO2max 的训练响应度从 0% 到 +60% 都有,21 个基因位点解释 49% 的变异。这就是为什么\"努力的两兄弟跑出不同成绩\"——遗传响应度不同。</p>",
        "insert": """  <div class="callout ops">
    <div class="label">读完这节·这周你能做的 3 件事</div>
    <p><strong>① 测:</strong>找一段 1.6 公里平直路,做一次 Cooper 12 分钟全力跑。VO2max ≈ (距离米 - 504.9) / 44.73。跑 2400 米 ≈ 42,跑 2800 米 ≈ 51。或用 Garmin/Coros 跑表自动估算(误差 ±3)。</p>
    <p><strong>② 改:</strong>VO2max 拉升靠 HIIT。每周 1 次:5 × 3 分钟全力(配速对应 5K-3K 比赛速度),3 分钟慢跑恢复。坚持 6-8 周可见 5-10% 提升。</p>
    <p><strong>③ 看:</strong>每月重测 Cooper。8 周后没动 = 已逼近遗传天花板,重心转去练 RE(力量训练 + 跑姿优化)和 LT2(阈值跑)。</p>
  </div>

  <div class="callout you">
    <div class="label">放在你身上 · 一次 Cooper 12 分钟测试的体感剧本</div>
    <p>你 35 岁、体重 70 kg、平常 5:30/km 巡航。今早你站上跑道,深呼吸 3 次,启动跑表。目标:12 分钟内尽可能跑远。</p>
    <p><strong>0-2 min:</strong>你按 4:30/km 出发,感觉"还行"。心率 155,呼吸 3 步一吸。这一段你的 VO2 还在爬坡,τ 慢的人前 2 分钟其实欠氧——靠 PCr 和糖酵解补差额。</p>
    <p><strong>2-6 min:</strong>VO2 已经接近 100%。心率冲到 175,呼吸变成 2 步一吸。腿开始有"灌铅"感,但你还能维持配速。这一段你<em>真的在 VO2max</em>。</p>
    <p><strong>6-10 min:</strong>地狱区。心率 185,呼吸 1:1。你想减速——这就是 W' 储备(高于临界速度的有限"无氧零钱")被掏到底的信号。腿酸 + 脑模糊 + 只想停下,意志 vs 生理在角力。</p>
    <p><strong>10-12 min:</strong>有人会"加速冲刺"——这其实是大脑保留的安全余量被放出来。最后 30 秒拼命,跑表显示 12:00,你倒在终点。距离 2580 米。算出来:VO2max ≈ (2580-504.9)/44.73 ≈ 46。<em>把这个数字记下来,8 周后再测一次,看跑步训练有没有真正在拉发动机。</em></p>
  </div>""",
    },
    # 10 · VO2 慢成分 ops
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p>在 5K–半马区间,慢成分是<em>\"为什么我能跑前 3 km 配速但跑不完全程\"</em>的代谢解释——你的 VO2 在缓慢漂向 VO2max,直到追上它就力竭。这也是为什么后段配速管理至关重要:留出余量给慢成分,否则它会替你做\"减速\"的决定。</p>",
        "insert": """  <div class="callout ops">
    <div class="label">读完这节·这周你能做的 3 件事</div>
    <p><strong>① 测:</strong>下一次 5K 比赛,把每公里配速记下来。如果第 5 公里比第 1 公里慢 15+ 秒/km,你就被慢成分"扣减"了;反之能保持均速则说明配速管理合理。</p>
    <p><strong>② 改:</strong>5K-10K 配速训练里加 progressive run:每公里加快 5 秒,最后 1 公里全力。训练身体在 VO2 慢成分中维持配速能力。</p>
    <p><strong>③ 看:</strong>用跑表看 HR 漂移——同样配速下,30 分钟内心率漂移 < 5 bpm 说明 VO2 慢成分小,体能足。> 10 bpm 说明你已经被慢成分拖到上限,得练 LT2 或减强度。</p>
  </div>""",
    },
    # 11 · 4.14 速查表 action-col
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"lead\">把这一章的所有概念回到地面,这里是把\"代谢区间\"翻译成具体训练目的的速查表。下一章 Ch5 会讲心肺系统怎么响应这些刺激,Ch10 会讲怎么把它们组装成完整训练计划。</p>",
        "insert": """  <div class="callout ops">
    <div class="label">本周怎么做 · 区间-动作-体感速查</div>
    <p><strong>Z1 恢复:</strong> 30-45 min 慢跑,能哼歌。比赛后第二天最该做。</p>
    <p><strong>Z2 基础:</strong> 周末早 90-150 min,能边跑边讲整句话。这是 80/20 训练里那"80%"。</p>
    <p><strong>Z3 灰区:</strong> 60-90 min 马拉松配速,只能讲短句。<em>少做</em>——多数业余跑者卡在这里出不来。</p>
    <p><strong>Z4 阈值:</strong> 20-40 min 单段或 4 × 8 min,接近半马配速,1 小时全力上限。每周 1 次。</p>
    <p><strong>Z5 间歇:</strong> 5 × 3-5 min 接近 5K-3K 配速,等长慢跑恢复。每周 1 次,赛季前期减半。</p>
    <p><strong>Z6 神经:</strong> 8-12 × 30-60 s 全力冲刺,3 分钟慢走恢复。短跑技术 + PCr 系统。每 2-3 周 1 次。</p>
  </div>""",
    },
    # 12 · 章末 protocol
    {
        "file": "chapters/ch04.html",
        "anchor": "  <p class=\"ref\">主要参考:[Brooks 2018 · Cell Metab][Brooks & Fahey 2005][Joyner & Coyle 2008 · J Physiol][Joyner 1991 · J Appl Physiol][Cavagna 1976][Beattie 2014][Blagrove 2018][Bassett & Howley 2000][Bouchard HERITAGE 1998][Hawley & Leckey 2015]</p>",
        "insert": """  <div class="callout protocol">
    <div class="label">PROTOCOL · 本章关键操作清单</div>

    <h4>协议 1 · Cooper 12 分钟测试推 VO2max</h4>
    <ol>
      <li><strong>测什么:</strong> 12 分钟全力跑的距离 → 反推 VO2max</li>
      <li><strong>工具:</strong> 跑表 + 400m 标准跑道(或一段平直无干扰路),热身 10 min</li>
      <li><strong>步骤:</strong> 启动跑表 → 全力均速 12 分钟 → 记录总距离 → VO2max ≈ (距离 - 504.9) / 44.73</li>
      <li><strong>频率:</strong> 每 6-8 周 1 次,训练初期可月度</li>
      <li><strong>判读:</strong> 业余男性 45-55 / 业余女性 38-48 算合格;每 8 周涨 2-4 算正常进步;连续 12 周不涨说明遗传天花板临近,重心转 RE/LT2</li>
    </ol>
    <div class="stop">测试中胸痛、晕厥前兆、心律明显不齐 → 立刻停下并就医,不要"咬牙过去"</div>

    <h4>协议 2 · 30 分钟全力跑推 LT2</h4>
    <ol>
      <li><strong>测什么:</strong> 30 分钟可持续最高配速 → LT2 配速;后 20 分钟平均心率 → LTHR(乳酸阈心率)</li>
      <li><strong>工具:</strong> 跑表(开启秒级配速 + 心率)+ 一段 8-10 km 平直路</li>
      <li><strong>步骤:</strong> 热身 15 min Z2 → 全力均速跑 30 min(不能后半段崩)→ 记录全程平均配速 + 后 20 min 平均心率</li>
      <li><strong>频率:</strong> 每 8-12 周 1 次</li>
      <li><strong>判读:</strong> LTHR 反推 Z1-Z5:Z1 < 80% LTHR / Z2 80-89% / Z3 90-94% / Z4 95-100% / Z5 > 100%。多数业余跑者会发现自己平常 Easy 跑其实在 Z3 灰区</li>
    </ol>
    <div class="stop">测试中出现明显跛行、关节锐痛、胸闷 → 停下,这不是"还能咬住"的疲劳</div>

    <h4>协议 3 · Z2 巡航空腹脂肪氧化测试</h4>
    <ol>
      <li><strong>测什么:</strong> 空腹晨跑 60 min Z2 后的精神状态与配速维持能力 → 间接判断脂肪氧化能力</li>
      <li><strong>工具:</strong> 跑表(心率带必备,腕表光学心率在低强度下不够准)</li>
      <li><strong>步骤:</strong> 起床后只喝水 → 30 min 内开跑 → 严格保持心率在 LT1 心率以下(约 70-75% HRmax)→ 跑满 60 min</li>
      <li><strong>频率:</strong> 每周 1 次,马拉松备战期 12 周</li>
      <li><strong>判读:</strong> 60 min 后能轻松完成、配速无显著下降 → 脂肪氧化通路已训练好。20-40 min 就明显疲惫、需要补糖 → 脂肪利用率低,后续多加 Z2 跑量</li>
    </ol>
    <div class="stop">头晕、出冷汗、视野模糊 = 低血糖前兆 → 立刻补糖(15-25g 快速碳水)并停跑;反复出现说明肝糖原储备过低,不适合空腹训练</div>

  </div>""",
    },
]
