import time


print('Check Thing Is Halal OR Haram ')
inp = input('Want To Check: ')
print(f'..... Checking: {inp} .....')
time.sleep(5)

def Quran(inp):
    if inp in ['playing games' , 'programming' , 'studying','sleep','rest']:
        return f'{inp} Is Halal'
    elif inp in ['spending money','watch movie' , 'songs']:
        return f'{inp} Is Not A Good Gesture'

    else:
        return f'{inp} Is Haram...!'

def catch(Quran):
    print( Quran)
catch(Quran(inp))