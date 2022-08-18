import torch

import utils
from cleaner import japanese_cleaner
from sequence import get_text

hps = utils.get_hparams_from_file("./configs/ljs_base.json")
model = torch.jit.load('./net_g.pt')

torch.set_grad_enabled(False)
longtext = "どうしてこうなるんだろう。初めて、好きな人が出来た。一生ものの友だちができた。嬉しいことが二つ重なって。その二つの嬉しさが、また、たくさんの嬉しさを連れてきてくれて。夢のように幸せな時間を手に入れたはずなのに…なのに、どうして、こうなっちゃうんだろう。"

stn_tst = get_text(japanese_cleaner(longtext), hps)
x = stn_tst.unsqueeze(0)
x_lengths = torch.LongTensor([stn_tst.size(0)])

model(x, x_lengths)[0][0, 0].data.float().numpy().tobytes()
