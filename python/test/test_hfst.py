# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
import hfst_dev
import os.path
from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

from sys import version
if int(version[0]) > 2:
    def unicode(s, c):
        return s

types = []
if hfst_dev.HfstTransducer.is_implementation_type_available(hfst_dev.ImplementationType.TROPICAL_OPENFST_TYPE):
    types.append(hfst_dev.ImplementationType.TROPICAL_OPENFST_TYPE)
if hfst_dev.HfstTransducer.is_implementation_type_available(hfst_dev.ImplementationType.FOMA_TYPE):
    types.append(hfst_dev.ImplementationType.FOMA_TYPE)

for type in types:

    print('\n--- Testing implementation type %s ---\n' % hfst_dev.fst_type_to_string(type))

    hfst_dev.set_default_fst_type(type)

    tr1 = None
    tr2 = None
    tr3 = None

    type_ = hfst_dev.ImplementationType.TROPICAL_OPENFST_TYPE
    ostr = hfst_dev.HfstOutputStream(filename='foobar.hfst', type=type_)

    tr_ = hfst_dev.regex('{foo}:{bar}::0.5')
    tr_.convert(type_)

    ostr.write(tr_)
    ostr.write(tr_)
    ostr.flush()
    ostr.close()

    if not os.path.isfile('foobar.hfst'):
        raise RuntimeError('Missing file: foobar.hfst')

    istr = hfst_dev.HfstInputStream('foobar.hfst')
    numtr = 0
    try:
        tr1 = istr.read()
        numtr += 1
        tr2 = istr.read()
        numtr += 1
        tr3 = istr.read()
        numtr += 1
    except hfst_dev.exceptions.EndOfStreamException:
        pass
    except:
        raise RuntimeError(get_linenumber())
    istr.close()

    if numtr != 2:
        raise RuntimeError(get_linenumber())

    tr1.convert(hfst_dev.get_default_fst_type())
    tr2.convert(hfst_dev.get_default_fst_type())

    ostr = hfst_dev.HfstOutputStream(filename='foobar2.hfst')
    ostr.write(tr1)
    ostr.write(tr2)
    ostr.flush()
    ostr.close()

    TR1 = None
    TR2 = None
    TR3 = None

    istr = hfst_dev.HfstInputStream('foobar2.hfst')
    numtr = 0
    try:
        TR1 = istr.read()
        numtr += 1
        TR2 = istr.read()
        numtr += 1
        TR3 = istr.read()
        numtr += 1
    except hfst_dev.exceptions.EndOfStreamException:
        pass
    except:
        raise RuntimeError(get_linenumber())
    istr.close()

    if numtr != 2:
        raise RuntimeError(get_linenumber())
    
    if not (TR1.compare(tr1)):
        raise RuntimeError(get_linenumber())
    if not (TR2.compare(tr2)):
        raise RuntimeError(get_linenumber())

    # Copy constructor
    transducer = hfst_dev.HfstTransducer(TR1)
    if not (TR1.compare(transducer)):
        raise RuntimeError(get_linenumber())
    if not (transducer.compare(TR1)):
        raise RuntimeError(get_linenumber())

    # Read lexc from file
    tr = hfst_dev.compile_lexc_file('test.lexc')
    tr.insert_freely(tr1)
    tr.minimize()
    tr.insert_freely(('A','B'))
    tr.minimize()

    # Read lexc from string
    lexcstr = """
LEXICON Root
foo BAR ;
foo BAZ ;

LEXICON BAR
bar # ;

LEXICON BAZ
baz # ;
    """
    tr = hfst_dev.compile_lexc_script(lexcstr)
    res = hfst_dev.regex('[f o o b a r] | [f o o b a z]')
    assert(tr.compare(res))

    # Read sfst
    tr = hfst_dev.compile_sfst_file('test.sfstpl')
    assert(not (tr == None))

    # Substitute
    tr = hfst_dev.regex('a a:b b;')
    tr.substitute('a', 'A', input=True, output=False)
    eq = hfst_dev.regex('A:a A:b b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute('a', 'A', input=False, output=True)
    eq = hfst_dev.regex('a:A a:b b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute('a','A')
    eq = hfst_dev.regex('A A:b b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute(('a','b'),('A','B'))
    eq = hfst_dev.regex('a A:B b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute(('a','b'),(('A','B'),('B','C'),('C','D')))
    eq = hfst_dev.regex('a [A:B|B:C|C:D] b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute(('a','b'),(('A','B'),('B','C'),('C','D')))
    eq = hfst_dev.regex('a [A:B|B:C|C:D] b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute({'a':'A', 'b':'B', 'c':'C'})
    eq = hfst_dev.regex('A A:B B;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    tr.substitute({('a','a'):('A','a'), ('a','b'):('a','B'), ('c','c'):('C','c')})
    eq = hfst_dev.regex('A:a a:B b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    tr = hfst_dev.regex('a a:b b;')
    sub = hfst_dev.regex('[c:d]+;')
    tr.substitute(('a','b'),sub)
    eq = hfst_dev.regex('a [c:d]+ b;')
    if not (tr.compare(eq)):
        raise RuntimeError(get_linenumber())

    # push weights
    tr = hfst_dev.regex('[a::1 a:b::0.3 b::0]::0.7;')
    tr.push_weights_to_start()
    tr.push_weights_to_end()

    # set final weights
    tr = hfst_dev.regex('(a a:b (b));')
    tr.set_final_weights(0.1)
    tr.set_final_weights(0.4, True)

    # reading and writing in text format
    f = open('testfile_.att', 'w')
    f.write('0 1 foo bar 0.5\n\
0 1 fo ba 0.2\n\
0 1 f b 0\n\
1 2 baz baz\n\
2 0.1\n\
--\n\n')
    f.close()

    numtr = 0
    f = open('testfile_.att', 'r')
    try:
        while True:
            TR = hfst_dev.read_att_transducer(f)
            numtr += 1
    except hfst_dev.exceptions.EndOfStreamException:
        pass
    f.close()
    if numtr != 2:
        raise RuntimeError(get_linenumber())

    f = open('foo_att_prolog', 'w')
    f.write('-- in ATT format --\n')
    TR.write_att(f)
    f.write('-- in prolog format --\n')
    TR.write_prolog(f)
    f.close()

    fsm = hfst_dev.read_att_string(' 0\t 1 a b\n\
                                1 2 c   d 0.5\n\
2 \n\
2 3 \t\te f\n\
                                    3   0.3 ')
    #if not fsm.compare(hfst_dev.regex('a:b c:d::0.5 (e:f::0.3)')):
    #    raise RuntimeError('read_att_string failed')

    # Lookup and path extraction
    tr = hfst_dev.regex('foo:bar::0.5 | foo:baz')

    f = open('foo', 'w')
    try:
        print(tr.lookup('foo', max_number=5, output='text'), file=f)
    except hfst_dev.exceptions.FunctionNotImplementedException:
        TR = hfst_dev.HfstTransducer(tr)
        TR.convert(hfst_dev.ImplementationType.HFST_OLW_TYPE)
        print(TR.lookup('foo', max_number=5, output='text'), file=f)

    tr_ = tr.copy()
    tr.lookup_optimize()
    tr.lookup('foo', max_number=5, output='text', file=f)
    tr.remove_optimization()
    assert(tr.compare(tr_))

#  def lookup_fd(self, lookup_path, **kwargs):
#      max_weight = None
#      infinite_cutoff = -1 # Is this right?
#      output='dict' # 'dict' (default), 'text', 'raw'


    fsm = hfst_dev.HfstIterableTransducer(tr)
    print(fsm.lookup((('foo'))), file=f)

    print(tr.extract_paths(obey_flags='True', filter_flags='False', max_number=3, output='dict'), file=f)

    def test_fst(input, result):
        tr1_ = hfst_dev.fst(input)
        tr2_ = hfst_dev.regex(result)
        if not tr1_.compare(tr2_):
            raise RuntimeError('test_fst failed with input: ' + input)

    f.close()

    # Create automaton:
    # unweighted
    test_fst('foobar', '[f o o b a r]')
    test_fst(['foobar'], '[f o o b a r]')
    test_fst(['foobar', 'foobaz'], '[f o o b a [r|z]]')
    # with weights
    test_fst(('foobar', 0.3), '[f o o b a r]::0.3')
    test_fst([('foobar', 0.5)], '[f o o b a r]::0.5')
    test_fst(['foobar', ('foobaz', -2)], '[ f o o b a [r|[z::-2]] ]')
    # Special inputs
    test_fst('*** FOO ***', '{*** FOO ***}')

    foo = hfst_dev.fst('')
    eps = hfst_dev.epsilon_fst()
    assert(foo.compare(eps))
    #try:
    #    foo = hfst_dev.fst('')
    #    raise RuntimeError(get_linenumber())
    #except RuntimeError as e:
    #    if not e.__str__() == 'Empty word.':
    #        raise RuntimeError(get_linenumber())

    # Create transducer:
    # unweighted
    test_fst({'foobar':'foobaz'}, '[f o o b a r:z]')
    test_fst({'foobar':['foobar','foobaz']}, '[f o o b a [r|r:z]]')
    test_fst({'foobar':('foobar','foobaz')}, '[f o o b a [r|r:z]]')
    test_fst({'foobar':'foobaz', 'FOOBAR':('foobar','FOOBAR'), 'Foobar':['Foo','bar','Foobar']}, '[f o o b a r:z] | [F O O B A R] | [F:f O:o O:o B:b A:a R:r] | [F o o b:0 a:0 r:0] | [F:b o:a o:r b:0 a:0 r:0] | [F o o b a r]')

    # with weights
    test_fst({'foobar':('foobaz', -1)}, '[f o o b a r:z]::-1')
    test_fst({'foobar':['foobar',('foobaz',-2.0)]}, '[f o o b a [r|r:z::-2.0]]')
    test_fst({'foobar':('foobar',('foobaz',3.5))}, '[f o o b a [r|r:z::3.5]]')
    test_fst({'foobar':('foobaz', -1), 'FOOBAR':('foobar',('FOOBAR', 2)), 'Foobar':[('Foo',2.5),'bar',('Foobar',0.3)]}, '[f o o b a r:z]::-1 | [F O O B A R]::2 | [F:f O:o O:o B:b A:a R:r] | [F o o b:0 a:0 r:0]::2.5 | [F:b o:a o:r b:0 a:0 r:0] | [F o o b a r]::0.3')

    # Special inputs
    test_fst({'*** FOO ***':'+++ BAR +++'}, '{*** FOO ***}:{+++ BAR +++}')

    foo = hfst_dev.fst({'':'foo'})
    tr = hfst_dev.regex('0:{foo}')
    assert(foo.compare(tr))
    foo = hfst_dev.fst({'foo':''})
    tr = hfst_dev.regex('{foo}:0')
    assert(foo.compare(tr))
    #try:
    #    foo = hfst_dev.fst({'':'foo'})
    #    raise RuntimeError(get_linenumber())
    #except RuntimeError as e:
    #    if not e.__str__() == 'Empty word.':
    #        raise RuntimeError(get_linenumber())
    #try:
    #    foo = hfst_dev.fst({'foo':''})
    #    raise RuntimeError(get_linenumber())
    #except RuntimeError as e:
    #    if not e.__str__() == 'Empty word.':
    #        raise RuntimeError(get_linenumber())

    # Tokenized input
    def test_tokenized(tok, pathin, pathout, exp, weight=0):
        tokenized = None
        if (pathout == None):
            tokenized = tok.tokenize_one_level(pathin)
        else:
            tokenized = tok.tokenize(pathin, pathout)
        if not hfst_dev.tokenized_fst(tokenized, weight).compare(hfst_dev.regex(exp)):
            if pathout == None:
                raise RuntimeError('test_tokenized failed with input: ' + pathin)
            else:
                raise RuntimeError('test_tokenized failed with input: ' + pathin + ", " + pathout)

    tok = hfst_dev.HfstTokenizer()

    test_tokenized(tok, 'foobar', None, '[f o o b a r]')
    test_tokenized(tok, 'foobar', 'foobar', '[f o o b a r]')
    test_tokenized(tok, 'foobar', 'foobaz', '[f o o b a r:z]')
    test_tokenized(tok, 'fööbär?', None, '[f ö ö b ä r "?"]')
    test_tokenized(tok, 'fööbär?', 'fööbär?', '[f ö ö b ä r "?"]')
    test_tokenized(tok, 'fööbär?', 'fööbäz!', '[f ö ö b ä r:z "?":"!"]::0.5', 0.5)

    test_tokenized(tok, 'foo', None, '[f o o]')
    test_tokenized(tok, 'foobar', 'foo', '[f o o b:0 a:0 r:0]')
    test_tokenized(tok, 'bar', 'foobaz', '[b:f a:o r:o 0:b 0:a 0:z]')
    test_tokenized(tok, 'bär?', None, '[b ä r "?"]')
    test_tokenized(tok, 'fööbär?', 'bär?', '[f:b ö:ä ö:r b:"?" ä:0 r:0 "?":0]')
    test_tokenized(tok, 'bär?', 'fööbäz!', '[b:f ä:ö r:ö "?":b 0:ä 0:z 0:"!"]')

    tok.add_skip_symbol('fö')
    tok.add_multichar_symbol('föö')
    tok.add_multichar_symbol('fööbär')

    test_tokenized(tok, 'föbär', None, '[b ä r]')
    test_tokenized(tok, 'fööbär', None, '[fööbär]')
    test_tokenized(tok, 'föfööfö', None, '[föö]')

    test_tokenized(tok, 'föbär', 'foofö', '[b:f ä:o r:o]')
    test_tokenized(tok, 'fööbär', 'föbar', '[fööbär:b 0:a 0:r]')
    test_tokenized(tok, 'föfööfö', 'föföföföö', '[föö]')

    tok = hfst_dev.HfstTokenizer()
    tok.add_skip_symbol('?')
    tok.add_skip_symbol(' ')
    test_tokenized(tok, 'How is this tokenized?', None, '[H o w i s t h i s t o k e n i z e d]')
    tok.add_skip_symbol(' is ')
    test_tokenized(tok, 'How is this tokenized?', None, '[H o w t h i s t o k e n i z e d]')

    tok = hfst_dev.HfstTokenizer()
    tok.add_multichar_symbol(hfst_dev.EPSILON) # TODO: should this be included by default???
    test_tokenized(tok, '@_EPSILON_SYMBOL_@foo', None, '[f o o]')

    if not hfst_dev.tokenized_fst([(hfst_dev.EPSILON,'b'),('f','a'),('o','a'),('o','r')]).compare(hfst_dev.regex('[0:b f:a o:a o:r]')):
        raise RuntimeError(get_linenumber())

    # Is this ok???
    if not hfst_dev.regex('"' + hfst_dev.EPSILON + '"').compare(hfst_dev.regex('[0]')):
        raise RuntimeError(get_linenumber())
    if not hfst_dev.regex('"' + hfst_dev.IDENTITY + '"').compare(hfst_dev.regex('[?]')):
        raise RuntimeError(get_linenumber())
    if not hfst_dev.regex('"' + hfst_dev.UNKNOWN + '":"' + hfst_dev.UNKNOWN + '"').compare(hfst_dev.regex('[?:?]')):
        raise RuntimeError(get_linenumber())

    # other python functions
    if not hfst_dev.empty_fst().compare(hfst_dev.regex('[0-0]')):
        raise RuntimeError(get_linenumber())
    if not hfst_dev.epsilon_fst().compare(hfst_dev.regex('[0]')):
        raise RuntimeError(get_linenumber())
    if not hfst_dev.epsilon_fst(-1.5).compare(hfst_dev.regex('[0]::-1.5')):
        raise RuntimeError(get_linenumber())

    # Non-ascii characters and unknowns/identities
    tr1 = hfst_dev.regex('Ä:é å ?;')
    tr2 = hfst_dev.regex('? Ö;')
    tr1.concatenate(tr2)
    result = hfst_dev.regex('Ä:é å [Ä|é|å|Ö|?] [Ä|é|å|Ö|?] Ö;')
    if not tr1.compare(result):
        raise RuntimeError(get_linenumber())

    tr1 = hfst_dev.regex('ñ ?:á;')
    tr2 = hfst_dev.regex('Ê:?;')
    tr1.concatenate(tr2)
    result = hfst_dev.regex('ñ [ñ:á|á|Ê:á|?:á] [Ê:ñ|Ê|Ê:á|Ê:?];')
    if not tr1.compare(result):
        raise RuntimeError(get_linenumber())

    # Other functions (TODO: more extensixe checks)
    tr = hfst_dev.regex('[foo]|[foo bar]|[f o o bar baz]')
    if not tr.longest_path_size() == 5:
        raise RuntimeError(get_linenumber())
    result = tr.extract_longest_paths()
    if not len(result) == 1:
        raise RuntimeError(get_linenumber())
    result = tr.extract_shortest_paths()
    if not len(result) == 1:
        raise RuntimeError(get_linenumber())

    # XfstCompiler
    if int(version[0]) > 2:
        import io
        msg = io.StringIO()
        if hfst_dev.compile_xfst_file('test_pass.xfst', verbosity=0, output=msg, error=msg) != 0:
            raise RuntimeError(get_linenumber())
        if hfst_dev.compile_xfst_file('test_fail.xfst', verbosity=0, output=msg, error=msg) == 0:
            raise RuntimeError(get_linenumber())
        if hfst_dev.compile_xfst_file('test_fail.xfst', quit_on_fail=False, verbosity=0, output=msg, error=msg) != 0:
            raise RuntimeError(get_linenumber())

    # regex compiler
    import io
    msg = io.StringIO()
    msg.write(unicode('This is the error message:\n', 'utf-8'))
    tr = hfst_dev.regex('foo\\', error=msg)
    if (tr == None):
        msg.write(unicode('This was the error message.\n', 'utf-8'))
        # print(msg.getvalue())
    import sys
    msg = sys.stdout
    tr = hfst_dev.regex('foo\\', error=msg)

    # lexc compiler
    msg = io.StringIO()
    tr = hfst_dev.compile_lexc_file('test.lexc', output=msg, verbosity=2)
    # print('This is the output from lexc:')
    # print(msg.getvalue())

    # default constructor
    tr = hfst_dev.HfstTransducer()
    assert(tr.compare(hfst_dev.empty_fst()))

    defs = {'foo':hfst_dev.regex('Foo'), 'bar':hfst_dev.regex('Bar')}
    tr = hfst_dev.regex('foo bar', definitions=defs)
    assert(tr.compare(hfst_dev.regex('Foo Bar')))
    tr = hfst_dev.regex('foo bar')
    assert(tr.compare(hfst_dev.regex('foo bar')))

# print('\n--- Testing HfstIterableTransducer ---\n')

# Create basic transducer, write it to file, read it, and test equivalence
fsm = hfst_dev.HfstIterableTransducer()
fsm.add_state(0)
fsm.add_state(1)
fsm.set_final_weight(1, 0.3)
tr = hfst_dev.HfstTransition(1, 'foo', 'bar', 0.5)
fsm.add_transition(0, tr)
fsm.add_transition(0, 0, 'baz', 'baz')
fsm.add_transition(0, 0, 'baz', 'BAZ', 0.1)

f = open('foo_basic', 'w')
fsm.write_att(f)
f.close()

f = open('foo_basic', 'r')
fsm2 = hfst_dev.HfstIterableTransducer(hfst_dev.read_att_transducer(f, hfst_dev.EPSILON))
f.close()

# Modify weights of a basic transducer
fsm = hfst_dev.HfstIterableTransducer()
fsm.add_state(0)
fsm.add_state(1)
fsm.set_final_weight(1, 0.3)
fsm.add_transition(0, 0, 'baz', 'baz')
arcs = fsm.transitions(0)
arcs[0].set_weight(0.5)
arcs = fsm.transitions(0)
assert(arcs[0].get_weight() == 0.5)

# comparison can fail because of rounding
#for type in types:
#    FSM = hfst_dev.HfstTransducer(fsm, type)
#    FSM2 = hfst_dev.HfstTransducer(fsm2, type)
#
#    if not (FSM.compare(FSM2)):
#        raise RuntimeError(get_linenumber())
#
# this test does not assert anything
#for type in types:
#    FSM.convert(type)
#    Fsm = hfst_dev.HfstIterableTransducer(FSM)
#    FSM2.convert(type)
#    Fsm2 = hfst_dev.HfstIterableTransducer(FSM2)


# Print basic transducer
fsm = hfst_dev.HfstIterableTransducer()
for state in [0,1,2]:
    fsm.add_state(state)
fsm.add_transition(0,1,'foo','bar',1)
fsm.add_transition(0,1,'foo','BAR',2)
fsm.add_transition(1,2,'baz','baz',0)
fsm.set_final_weight(2,0.5)

# Different ways to print the transducer
f = open('foo', 'w')
for state in fsm.states():
    for arc in fsm.transitions(state):
        print('%i ' % (state), end='', file=f)
        print(arc, file=f)
    if fsm.is_final_state(state):
        print('%i %f' % (state, fsm.get_final_weight(state)), file=f )

for state, arcs in enumerate(fsm):
    for arc in arcs:
        print('%i ' % (state), end='', file=f)
        print(arc, file=f)
    if fsm.is_final_state(state):
        print('%i %f' % (state, fsm.get_final_weight(state)), file=f)

index=0
for state in fsm.states_and_transitions():
    for transition in state:
        print('%u\t%u\t%s\t%s\t%.2f' % (index, transition.get_target_state(), transition.get_input_symbol(), transition.get_output_symbol(), transition.get_weight()), file=f)
    if fsm.is_final_state(index):
        print('%s\t%.2f' % (index, fsm.get_final_weight(index)), file=f)
    index = index + 1

print(fsm, file=f)
f.close()

tr = hfst_dev.HfstIterableTransducer(hfst_dev.regex('foo'))
tr.substitute({'foo':'bar'})
tr.substitute({('foo','foo'):('bar','bar')})

tr = hfst_dev.fst({'foo':'bar'})
fst = hfst_dev.HfstIterableTransducer(tr)
fsa = hfst_dev.fst_to_fsa(fst, '^')
fst = hfst_dev.fsa_to_fst(fsa, '^')
TR = hfst_dev.HfstTransducer(fst)
assert(TR.compare(tr))

tr = hfst_dev.regex('{foo}:{bar}|{FOO}:{BAR}')
fsm = hfst_dev.HfstIterableTransducer(tr)
net = fsm.states_and_transitions()
for state in net:
    for arc in state:
        arc.set_input_symbol(arc.get_input_symbol() + '>')
        arc.set_output_symbol('<' + arc.get_output_symbol())
        arc.set_weight(arc.get_weight() - 0.5)

for state, arcs in enumerate(fsm):
    for arc in arcs:
        arc.set_input_symbol('<' + arc.get_input_symbol())
        arc.set_output_symbol(arc.get_output_symbol() + '>')
        arc.set_weight(arc.get_weight() - 1.5)

for state in fsm:
    for arc in state:
        arc.set_input_symbol('' + arc.get_input_symbol() + '')
        arc.set_output_symbol('' + arc.get_output_symbol() + '')
        arc.set_weight(arc.get_weight() - 0.5)

tr = hfst_dev.regex('[["<f>" "<o>" "<o>"]:["<b>" "<a>" "<r>"]|["<F>" "<O>" "<O>"]:["<B>" "<A>" "<R>"]]::-7.5')
assert(not (tr == None))
TR = hfst_dev.HfstTransducer(fsm)
assert(TR.compare(tr))
