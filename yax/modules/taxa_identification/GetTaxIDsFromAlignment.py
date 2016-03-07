def analyze_sam_file(sam_fp, nm_max, taxids_of_interest):
    ###########################################################################
    ###########################################################################
    with open(sam_fp, 'r') as sam_file:
        sam_lines = sam_file.readlines()

    for sam_line in sam_lines:
        if sam_line[0] == "@":
            continue

        this_line = sam_line.split("\t")
        # checks for soft clipping and ignores any alignments where it is found
        if "S" in this_line[5]:
            # print("UPDATE_FROM_SAM: SOFT CLIPPING BAD, line ignored")
            continue

        bit = decode_bit_flag(this_line[1])
        if bit == "unmapped":
            # print("Found a read that did not map")
            continue

        nm = 0
        for tag in this_line[10:-1]:
            if tag[:2] == "NM":
                # print(tag)
                nm = int(tag.split(":")[2])
        if nm > nm_max:
            continue

        ref_id = this_line[2].split("|")[0]

        taxids_of_interest.add(ref_id)

    return taxids_of_interest


def decode_bit_flag(bit_flag):
    ###########################################################################
    #  Bit flag is turned into binary and individual bits are examined to
    # determine flag interpretation
    ###########################################################################
    # Flag		Description
    # 00000000001	the read is paired in sequencing
    # 00000000010	the read is mapped in a proper pair
    # 00000000100	the query sequence itself is unmapped
    # 00000001000	the mate is unmapped
    # 00000010000   strand of the query (1 for reverse)
    # 00000100000	strand of the mate
    # 00001000000	the read is the first read in a pair
    # 00010000000	the read is the second read in a pair
    # 00100000000	the taxa_identification is not primary
    # 01000000000	the read fails platform/vendor quality checks
    # 10000000000	the read is either a PCR or an optical duplicate
    bit_x = bin(int(bit_flag))[2:]
    bit = "0" * (12 - len(bit_x)) + bit_x
    strand = "positive"

    if bit[9] == "1":
        return "unmapped"
    # if bit[0] == "1":
    #     return "quality"
    if bit[7] == "1":
        strand = "negative"
    return strand
