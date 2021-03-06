from subprocess import PIPE, Popen

def tag(sentence):
    p = Popen("sh run.sh".split(),stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd="question-dir/11611-Falcons/generation/SupersenseTagger" )
    answer = p.communicate(sentence)
    ret = []
    for entry in answer[0].split("\n"):
        tags = entry.split("\t")
        if len(tags) > 2:
            actual_tags = tags[2].split("-")
            if len(actual_tags) < 2:
                ret.append("0")
            else:
                ret.append(actual_tags[1])
    return ret

def main():
    print tag("English is a West Germanic language that was first spoken in early medieval England")

if __name__=="__main__":main()
