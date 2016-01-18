

def batch(self, iterable, batch_size=15000):
    data_list = list(iterable)
    data_size = len(data_list)
    for slice_size in range(0, size, batch_size):
        yield data_list[slice_size:min(slice_size + batch_size, data_size)]
