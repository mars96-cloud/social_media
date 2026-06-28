(() => {
  const body = document.querySelectorAll('[contenteditable="true"]')[2];
  if (!body) {
    return JSON.stringify({ status: 'no-body' });
  }

  const img382 = '<section style="text-align:center;" nodeleaf=""><img src="https://mmbiz.qpic.cn/mmbiz_jpg/v4OiaqyicAPfhy9ftWvmrAQrBkUEGTHjP2cR4Mt7Zc6k8AKQOtMbSDCg5p0KTMEN21EGBa4AO3sic1kXzfdvic9W6qRJGpIYqC6icdibVdAmfeicmo/640?wx_fmt=jpeg&from=appmsg" data-src="https://mmbiz.qpic.cn/mmbiz_jpg/v4OiaqyicAPfhy9ftWvmrAQrBkUEGTHjP2cR4Mt7Zc6k8AKQOtMbSDCg5p0KTMEN21EGBa4AO3sic1kXzfdvic9W6qRJGpIYqC6icdibVdAmfeicmo/640?wx_fmt=jpeg&from=appmsg" class="rich_pages wxw-img js_insertlocalimg" data-ratio="0.56171875" data-s="300,640" data-type="jpeg" data-w="1280" type="block" data-imgfileid="100006382" data-aistatus="1" contenteditable="false"><img class="ProseMirror-separator" alt=""><br class="ProseMirror-trailingBreak"></section>';
  const img383 = '<section style="text-align:center;" nodeleaf=""><img src="https://mmbiz.qpic.cn/mmbiz_jpg/v4OiaqyicAPfh5MruV5zpQibaFGdrQzwpOt5LfOicBhUkEDrcRz8GfSOwpbOiapTQ685UHegzyicWic2t9QD8kEf9h0g0NuPMiaeW7Lr7DgY33DY3y8/640?wx_fmt=jpeg&from=appmsg" data-src="https://mmbiz.qpic.cn/mmbiz_jpg/v4OiaqyicAPfh5MruV5zpQibaFGdrQzwpOt5LfOicBhUkEDrcRz8GfSOwpbOiapTQ685UHegzyicWic2t9QD8kEf9h0g0NuPMiaeW7Lr7DgY33DY3y8/640?wx_fmt=jpeg&from=appmsg" class="rich_pages wxw-img js_insertlocalimg" data-ratio="0.56171875" data-s="300,640" data-type="jpeg" data-w="1280" type="block" data-imgfileid="100006383" data-aistatus="1" contenteditable="false"><img class="ProseMirror-separator" alt=""><br class="ProseMirror-trailingBreak"></section>';
  const img384 = '<section style="text-align:center;" nodeleaf=""><img src="https://mmbiz.qpic.cn/sz_mmbiz_jpg/v4OiaqyicAPfjxibRsd52h6rff307zuSqP3KI6YiaZT1r5bHRcxCu9gkUB0Ht251icjRvtico1Uf7QT0V9gG6bfqO6ibibtDnpia2iaiaicme1MlPNA8ss4/640?wx_fmt=jpeg&from=appmsg" data-src="https://mmbiz.qpic.cn/sz_mmbiz_jpg/v4OiaqyicAPfjxibRsd52h6rff307zuSqP3KI6YiaZT1r5bHRcxCu9gkUB0Ht251icjRvtico1Uf7QT0V9gG6bfqO6ibibtDnpia2iaiaicme1MlPNA8ss4/640?wx_fmt=jpeg&from=appmsg" class="rich_pages wxw-img js_insertlocalimg" data-ratio="0.56171875" data-s="300,640" data-type="jpeg" data-w="1280" type="block" data-imgfileid="100006384" data-aistatus="1" contenteditable="false"><img class="ProseMirror-separator" alt=""><br class="ProseMirror-trailingBreak"></section>';

  const p = (text, style = '') => `<section${style ? ` style="${style}"` : ''}><span leaf="">${text}</span></section>`;

  const html = [
    p('一、为什么很多人用了 AI 还是没提效', 'margin-top: 18px; margin-bottom: 8px;'),
    p('先看结论：', 'margin-top: 10px; margin-bottom: 6px;'),
    p('很多人不是不会用 AI，而是一直停留在“点状使用”的阶段。'),
    p('这两年，很多人都已经接触过 AI。'),
    p('会问问题，会让它帮忙写几段话，会拿它查资料，甚至还收藏了一堆提示词和教程。可如果你认真回头看一眼，就会发现一个很扎心的现实：'),
    img382,
    p('你学过不少工具，也试过不少玩法，但真正稳定省下来的时间、稳定多出来的结果，可能并没有你想象中那么多。'),
    p('问题通常不是你不够努力，也不是工具不够强。'),
    p('真正的问题是，你一直没有自己的第一条工作流。'),
    p('很多人现在用 AI，还是一种“点状使用”。'),
    p('今天看到一个工具，就去试一下。明天看到一个新功能，再玩一下。后天又存了一堆提示词，感觉自己学了很多。但这些动作大多是零散的，并没有真正接进你的日常产出里。'),
    p('所以你会经常陷入一种状态：学的时候很兴奋，用的时候很随机，做的时候很混乱，最后回头看，真正留下来的变化并不多。'),
    p('这也是为什么很多人会有一种挫败感：'),
    p('我明明已经在用 AI 了，为什么还是没怎么提效？'),
    p('答案往往不是你不会用，而是你还没有把它用成系统。'),
    p('二、真正缺的不是更多工具，而是第一条工作流', 'margin-top: 22px; margin-bottom: 8px;'),
    p('真正的问题是：', 'margin-top: 10px; margin-bottom: 6px;'),
    p('你现在最缺的，通常不是第 18 个 AI 工具，也不是更复杂的自动化。'),
    p('你真正缺的，是先把一件高频、重复、容易卡住的事，拆成一条能反复跑的流程。'),
    p('什么叫工作流？'),
    img383,
    p('说白了，就是把一件原来总靠临场发挥的事，拆成几个固定环节。你知道从哪里开始，知道中间怎么推进，知道哪些环节适合交给 AI，也知道哪些判断必须自己来做。'),
    p('一旦这条流程跑通，AI 才会真正开始帮你省时间、稳结果、放大产出。'),
    p('比如内容创作这件事，很多人并不是不会写，而是每次都从零开始：'),
    p('今天写什么，怎么起标题，提纲怎么搭，正文怎么展开，发出去之前怎么收尾。'),
    p('如果这些环节每次都重新想一遍，再好的工具也只能局部帮你一把。'),
    p('但如果你先把内容生产拆成固定流程，再把 AI 嵌进去，整件事的手感会完全不同。你不是在临时救火，而是在跑一条已经搭起来的路。'),
    p('三、普通人该怎么开始搭第一条工作流', 'margin-top: 22px; margin-bottom: 8px;'),
    p('先把流程看明白：', 'margin-top: 10px; margin-bottom: 6px;'),
    p('第一条工作流，千万别一上来就追求复杂。'),
    p('普通人最适合的起点，不是做全自动，不是做 agent，也不是一口气串很多工具，而是先解决一个最常重复、最容易卡住、最能直接省时间的问题。'),
    p('你可以先问自己三个问题：'),
    img384,
    p('我每周都重复在做什么？'),
    p('哪一个环节最容易卡住？'),
    p('这个环节如果理顺了，最直接能帮我省下什么？'),
    p('只要这三个问题答得足够清楚，你的第一条工作流就能开始了。'),
    p('比如你总是卡在选题，就先搭选题工作流；总是卡在提纲，就先搭提纲工作流；总是卡在发布前收尾，就先搭发布工作流。'),
    p('先把一条高频动作跑顺，比什么都重要。'),
    p('因为一条工作流真正的价值，不只是提效。'),
    p('它会把你从“偶尔会用 AI”，带到“开始拥有自己的 AI 方法”。这两者之间，差得非常大。'),
    p('前者只是工具使用者，后者才开始变成流程拥有者。'),
    p('如果你现在也处在这种状态：'),
    p('学过一点 AI，知道它有用，但始终觉得自己没真正提效，也没真正把它变成结果。'),
    p('那我更建议你先停下来，认真搭出自己的第一条工作流。'),
    p('这一步做对了，后面很多问题，都会突然简单很多。'),
    p('最后别漏掉承接动作：', 'margin-top: 14px; margin-bottom: 6px;'),
    p('关注我，后面我会继续把“普通人最值得先搭的几条 AI 工作流”一条条拆开讲清楚。')
  ].join('');

  body.innerHTML = html;
  body.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: '' }));
  body.dispatchEvent(new Event('change', { bubbles: true }));

  return JSON.stringify({
    status: 'body-rewritten',
    text: body.innerText.slice(0, 300),
    html: body.innerHTML.slice(0, 1200)
  });
})();
