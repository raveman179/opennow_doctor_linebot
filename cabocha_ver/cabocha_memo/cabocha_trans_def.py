import CaboCha

def cabochaperse(sentence):
    c = CaboCha.Parser()
    tree =  c.parse(sentence)
# 形態素を結合しつつ[{c:文節, to:係り先id}]の形に変換する
    chunks = []
    text = ""
    toChunkId = -1
    for i in range(0, tree.size()):
        token = tree.token(i)
        if token.chunk != None:
            text = token.surface
            toChunkId = token.chunk.link 
        else:
            text = text + token.surface

    # 文末かchunk内の最後の要素のタイミングで出力
        if i == tree.size() - 1 or tree.token(i+1).chunk:
            chunks.append({'c': text, 'to': toChunkId})
    print(chunks)
    return chunks

s = ['2016年の診療は12月29日（受付終了13時30分）までとなります']

chunks = cabochaperse(s[0])

# 係り元→係り先の形式で出力する
for chunk in chunks:
    if chunk['to'] >= 0:
        print(chunk['c'] + " →　" + chunks[chunk['to']]['c'])

