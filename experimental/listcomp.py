[
    [None for stdin in [input('> ')] if not(
        loop.clear() if stdin=='exit' else(
            print('Unknown command') if (result.returncode != 0) else (
                loop.append(None) or print(result.stdout.decode('utf-8'))
                )
            for result in [subprocess.run(stdin,shell=True,stdout=subprocess.PIPE)]
            )
        )
     ]
    for loop in [[None]] for i in loop
    for subprocess in [__import__('subprocess')]
] and None
