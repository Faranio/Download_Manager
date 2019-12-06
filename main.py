import click
import requests
import threading


def Handler(start, end, url, filename):
	headers = {'Range': 'bytes=%d-%d' % (start, end)}
	r = requests.get(url, headers=headers, stream=True)
	
	with open(filename, 'r+b') as file:
		file.seek(start)
		var = file.tell()
		file.write(r.content)


@click.command(help="The download manager downloads the file from the specified URL under the specified name.")
@click.option('--number_of_threads', default=4, help='Number of threads to be used. Default is 4.')
@click.option('--name', type=click.Path(), help='Name of the file with extension.')
@click.argument('url', type=click.Path())
@click.pass_context
def download_file(context, url, name, number_of_threads):
	r = requests.head(url)
	
	if name:
		file_name = name
	else:
		file_name = url.split('/')[-1]
	
	try:
		file_size = int(r.headers['content-length'])
	except:
		print("Error! Invalid URL was provided!")
		return
	
	part = int(file_size) // number_of_threads
	file = open(file_name, "wb")
	file.write(b'\0' * file_size)
	file.close()
	
	for i in range(number_of_threads):
		start = part * i
		end = start + part
		
		t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url, 'filename': file_name})
		t.setDaemon(True)
		t.start()
		
		main_thread = threading.current_thread()
		
		for t in threading.enumerate():
			if t is main_thread:
				continue
			t.join()
		
	print("The file \'{}\' was downloaded.".format(file_name))


if __name__ == '__main__':
	download_file(obj={})
