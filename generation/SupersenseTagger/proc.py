from subprocess import PIPE, Popen

def tag(sentence):
    p = Popen("sh run.sh".split(),stdin=PIPE, stdout=PIPE, cwd="SupersenseTagger")
    answer = p.communicate(sentence)
    print answer
    ret = []
    for entry in answer[0].split("\n"):
        tags = entry.split("\t")
        if len(tags) > 2:
            ret.append(tags[2])
    return ret

def main():
    print tag("English is a West Germanic language that was first spoken in early medieval England")

if __name__=="__main__":main()