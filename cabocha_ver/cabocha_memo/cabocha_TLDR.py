# https://qiita.com/ayuchiy/items/c3f314889154c4efa71e より抜粋

import CaboCha

c = CaboCha.Parser()
# sentence = "太郎はこの本を二郎を見た女性に渡した。"
sentence = "9月3日（火）は職員健康診断のため休診致します。御了承ください。"

tree =  c.parse(sentence)
chunkId = 0
for i in range(0, tree.size()):
    token = tree.token(i)
    if token.chunk != None:
        print(chunkId, token.chunk.link, token.chunk.head_pos, token.chunk.func_pos, token.chunk.score)
        chunkId += 1

    print(token.surface, token.feature, token.ne)

print(type(token))
'''
tree
　└ token
　　　└ chunk　　　　　 ←ない場合(NULL)もある
　　　│　 └ link　　　 ←かかり先ID
　　　│　 └ head_pos 　←主辞(文節の中心となる単語)の位置
　　　│　 └ func_pos　 ←機能語(助詞等)の位置
　　　│　 └ score　　　←係り関係のスコア(大きい方が係りやすい)
　　　└ surface　　　　 ←形態素部分(元の文字列)
　　　└ feature　　　　 ←品詞や読みなど形態素の情報部分
　　　└ ne　　　　　　  ←？？

example
1 2 0 0 1.5095065832138062
この 連体詞,*,*,*,*,*,この,コノ,コノ None

一行目：chunkId, token.chunk.link, token.chunk.head_pos, token.chunk.func_pos, token.chunk.score
二行目：token.surface, token.feature, token.ne

http://njf.jp/cms/modules/xpwiki/?%E8%87%AA%E7%84%B6%E8%A8%80%E8%AA%9E%E8%A7%A3%E6%9E%90%2FCaboCha%E3%82%92python%E3%81%A7%E4%BD%BF%E3%81%86 より

コマンドラインで出力した場合

echo "これは私のもっている赤いペンです"|cabocha -f1
* 0 3D 0/1 -2.060711
これ	名詞,代名詞,一般,*,*,*,これ,コレ,コレ
は	助詞,係助詞,*,*,*,*,は,ハ,ワ
* 1 2D 0/1 2.120296
私	名詞,代名詞,一般,*,*,*,私,ワタシ,ワタシ
の	助詞,格助詞,一般,*,*,*,の,ノ,ノ
* 2 3D 0/2 -2.060711
もっ	動詞,自立,*,*,五段・タ行,連用タ接続,もつ,モッ,モッ
て	助詞,接続助詞,*,*,*,*,て,テ,テ
いる	動詞,非自立,*,*,一段,基本形,いる,イル,イル
* 3 -1D 1/2 0.000000
赤い	名詞,一般,*,*,*,*,赤井,アカイ,アカイ
ペン	名詞,一般,*,*,*,*,ペン,ペン,ペン
です	助動詞,*,*,*,特殊・デス,基本形,です,デス,デス
EOS

* 0 3D 0/1 -2.060711
を例にすると、各データの意味は以下の通りです。

最初の0は文節の通番。文頭なので0
3Dは数字の部分がその文節がかかっている通番。ここでは通番3の「赤いペンです」にかかっている。かかり先がなければ-1。よって文末は常に-1。Dの意味は資料がなく不明
0/1の主辞（文節の中心となる単語）と機能語（助詞など）の位置を示している。この例では「私」が主辞で「の」が機能語
次の小数値はかかりやすさの度合い

CaboCha編集は文を文節、つまり形態素の集まりに分解し解析するので、CaboCha編集のそれぞれの結果には複数の形態素が含まれます。
アスタリスクから始まる行の続きの行がその形態素です。
つまりこの通番0の結果には「これ」「は」の二つの形態素が含まれます。

'''