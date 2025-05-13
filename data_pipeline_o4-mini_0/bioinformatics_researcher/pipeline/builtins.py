def batch_reads(reads, batch_size=10000):
    batches = []
    for i in range(0, len(reads), batch_size):
        batches.append(reads[i:i+batch_size])
    return batches

def sort_reads(reads):
    return sorted(reads, key=lambda r: (r.get('chr'), r.get('pos')))

def group_reads(reads):
    groups = {}
    for r in reads:
        gene = r.get('gene')
        groups.setdefault(gene, []).append(r)
    return groups
