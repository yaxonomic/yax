def read_fasta_file(fasta_file_path):
    fasta_headers = []
    fasta_seqs = []
    seq = ""
    fasta_file_fh = open(fasta_file_path, 'r')

    for line in fasta_file_fh:
        if line[0] == ">":
            fasta_headers.append(line.rstrip().lstrip(">"))
            if seq != "":
                fasta_seqs.append(seq)
            seq = ""
        else:
            seq += line.rstrip("\n")
    fasta_seqs.append(seq)

    fasta_seqs = remove_illegal_characters(fasta_seqs)

    return fasta_headers, fasta_seqs
