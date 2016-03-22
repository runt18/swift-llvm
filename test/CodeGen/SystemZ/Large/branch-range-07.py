# Test 32-bit BRANCH RELATIVE ON COUNT in cases where some branches are out
# of range.
# RUN: python %s | llc -mtriple=s390x-linux-gnu | FileCheck %s

# Construct:
#
# loopN:
#   load of countN
#   ...
# loop0:
#   0xffd8 bytes, from MVIY instructions
#   conditional branch to main
# after0:
#   ...
#   decrement of countN
#   conditional branch to loopN
# afterN:
#
# Each load occupies 4 bytes.  Each decrement and branch occupies 4
# bytes if BRCT can be used, otherwise it occupies 10 bytes (AHI + BRCL).
# This means that loop 6 contains 5 * 4 + 0xffd8 + 5 * 4 == 0x10000 bytes
# and is therefore (just) in range.  Loop 7 is out of range.
#
# CHECK: brct {{%r[0-9]+}}
# CHECK: brct {{%r[0-9]+}}
# CHECK: brct {{%r[0-9]+}}
# CHECK: brct {{%r[0-9]+}}
# CHECK: brct {{%r[0-9]+}}
# CHECK: brct {{%r[0-9]+}}
# CHECK: ahi {{%r[0-9]+}}, -1
# CHECK: jglh
# CHECK: ahi {{%r[0-9]+}}, -1
# CHECK: jglh

branch_blocks = 8
main_size = 0xffd8

print 'define void @f1(i8 *%base, i32 *%counts) {'
print 'entry:'

for i in xrange(branch_blocks - 1, -1, -1):
    print '  %countptr{0:d} = getelementptr i32, i32 *%counts, i64 {1:d}'.format(i, i)
    print '  %initcount{0:d} = load i32 , i32 *%countptr{1:d}'.format(i, i)
    print '  br label %loop{0:d}'.format(i)
    
    print 'loop{0:d}:'.format(i)
    block1 = 'entry' if i == branch_blocks - 1 else 'loop{0:d}'.format((i + 1))
    block2 = 'loop0' if i == 0 else 'after{0:d}'.format((i - 1))
    print ('  %%count%d = phi i32 [ %%initcount%d, %%%s ],'
           ' [ %%nextcount%d, %%%s ]' % (i, i, block1, i, block2))

a, b = 1, 1
for i in xrange(0, main_size, 6):
    a, b = b, a + b
    offset = 4096 + b % 500000
    value = a % 256
    print '  %ptr{0:d} = getelementptr i8, i8 *%base, i64 {1:d}'.format(i, offset)
    print '  store volatile i8 {0:d}, i8 *%ptr{1:d}'.format(value, i)

for i in xrange(branch_blocks):
    print '  %nextcount{0:d} = add i32 %count{1:d}, -1'.format(i, i)
    print '  %test{0:d} = icmp ne i32 %nextcount{1:d}, 0'.format(i, i)
    print '  br i1 %test{0:d}, label %loop{1:d}, label %after{2:d}'.format(i, i, i)
    print ''
    print 'after{0:d}:'.format(i)

print '  ret void'
print '}'
