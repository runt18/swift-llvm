# Test 64-bit COMPARE LOGICAL AND BRANCH in cases where the sheer number of
# instructions causes some branches to be out of range.
# RUN: python %s | llc -mtriple=s390x-linux-gnu | FileCheck %s

# Construct:
#
# before0:
#   conditional branch to after0
#   ...
# beforeN:
#   conditional branch to after0
# main:
#   0xffcc bytes, from MVIY instructions
#   conditional branch to main
# after0:
#   ...
#   conditional branch to main
# afterN:
#
# Each conditional branch sequence occupies 12 bytes if it uses a short
# branch and 16 if it uses a long one.  The ones before "main:" have to
# take the branch length into account, which is 6 for short branches,
# so the final (0x34 - 6) / 12 == 3 blocks can use short branches.
# The ones after "main:" do not, so the first 0x34 / 12 == 4 blocks
# can use short branches.  The conservative algorithm we use makes
# one of the forward branches unnecessarily long, as noted in the
# check output below.
#
# CHECK: lgb [[REG:%r[0-5]]], 0(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL:\.L[^ ]*]]
# CHECK: lgb [[REG:%r[0-5]]], 1(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 2(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 3(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 4(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# ...as mentioned above, the next one could be a CLGRJL instead...
# CHECK: lgb [[REG:%r[0-5]]], 5(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 6(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 7(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL]]
# ...main goes here...
# CHECK: lgb [[REG:%r[0-5]]], 25(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL:\.L[^ ]*]]
# CHECK: lgb [[REG:%r[0-5]]], 26(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 27(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 28(%r3)
# CHECK: clgrjl %r4, [[REG]], [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 29(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 30(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 31(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]
# CHECK: lgb [[REG:%r[0-5]]], 32(%r3)
# CHECK: clgr %r4, [[REG]]
# CHECK: jgl [[LABEL]]

branch_blocks = 8
main_size = 0xffcc

print 'define void @f1(i8 *%base, i8 *%stop, i64 %limit) {'
print 'entry:'
print '  br label %before0'
print ''

for i in xrange(branch_blocks):
    next = 'before{0:d}'.format((i + 1)) if i + 1 < branch_blocks else 'main'
    print 'before{0:d}:'.format(i)
    print '  %bstop{0:d} = getelementptr i8, i8 *%stop, i64 {1:d}'.format(i, i)
    print '  %bcur{0:d} = load i8 , i8 *%bstop{1:d}'.format(i, i)
    print '  %bext{0:d} = sext i8 %bcur{1:d} to i64'.format(i, i)
    print '  %btest{0:d} = icmp ult i64 %limit, %bext{1:d}'.format(i, i)
    print '  br i1 %btest{0:d}, label %after0, label %{1!s}'.format(i, next)
    print ''

print '{0!s}:'.format(next)
a, b = 1, 1
for i in xrange(0, main_size, 6):
    a, b = b, a + b
    offset = 4096 + b % 500000
    value = a % 256
    print '  %ptr{0:d} = getelementptr i8, i8 *%base, i64 {1:d}'.format(i, offset)
    print '  store volatile i8 {0:d}, i8 *%ptr{1:d}'.format(value, i)

for i in xrange(branch_blocks):
    print '  %astop{0:d} = getelementptr i8, i8 *%stop, i64 {1:d}'.format(i, i + 25)
    print '  %acur{0:d} = load i8 , i8 *%astop{1:d}'.format(i, i)
    print '  %aext{0:d} = sext i8 %acur{1:d} to i64'.format(i, i)
    print '  %atest{0:d} = icmp ult i64 %limit, %aext{1:d}'.format(i, i)
    print '  br i1 %atest{0:d}, label %main, label %after{1:d}'.format(i, i)
    print ''
    print 'after{0:d}:'.format(i)

print '  ret void'
print '}'
