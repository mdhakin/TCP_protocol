# This Module sets up the state machine for the tcp connection

from statemachine import StateMachine, State
#pip install python-statemachine
class TrafficLightMachine(StateMachine):
    "A traffic light machine"
    green = State('Green', initial=True)
    yellow = State('Yellow')
    red = State('Red')

    cycle = green.to(yellow) | yellow.to(red) | red.to(green)
    begin = green.to(green) | yellow.to(green) | red.to(green)

    def on_enter_green(self):
        print('Valendo!')

    def on_enter_yellow(self):
        print('Calma, lá!')

    def on_enter_red(self):
        print('Parou.')



class usetl:
    def __init__(self):
        self.name = "Default"
        self.tl = TrafficLightMachine()



class tcpState(StateMachine):
    closed = State('closed', initial=True)
    listen = State('listen')
    syn_rcvd = State('syn_rcvd')
    syn_sent = State('syn_sent')
    estab = State('estab')
    fin_wait1 = State('fin_wait1')
    close_wait = State('close_wait')
    fin_wait2 = State('fin_wait2')
    closing = State('closing')
    last_ack = State('last_ack')
    time_wait = State('time_wait')

    to_closed = listen.to(closed) | time_wait.to(closed) | last_ack.to(closed) | syn_sent.to(closed)
    to_syn_sent = closed.to(syn_sent) | listen.to(syn_sent)
    to_listen = closed.to(listen)
    to_syn_rcvd = listen.to(syn_rcvd) | syn_sent.to(syn_rcvd)
    to_estab = syn_rcvd.to(estab) | syn_sent.to(estab)
    to_fin_wait1 = syn_rcvd.to(fin_wait1) | estab.to(fin_wait1)
    to_close_wait = estab.to(close_wait)
    to_fin_wait2 = fin_wait1.to(fin_wait2)
    to_closing = fin_wait1.to(closing)
    to_last_ack = close_wait.to(last_ack)
    to_time_wait = fin_wait2.to(time_wait) | closing.to(time_wait)
