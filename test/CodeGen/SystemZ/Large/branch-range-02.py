# Test normal conditional branches in cases where block alignments cause
# some branches to be out of range.
# RUN: python %s | llc -mtriple=s390x-linux-gnu -align-all-blocks=8 | FileCheck %s

# Construct:
#
# b0:
#   conditional branch to end
#   ...
# b<N>:
#   conditional branch to end
# b<N+1>:
#   conditional branch to b0
#   ...
# b<2*N>:
#   conditional branch to b0
# end:
#
# with N == 256 + 4.  The -align-all-blocks=8 option ensures that all blocks
# are 256 bytes in size.  The first 4 blocks and the last 4 blocks are then
# out of range.
#
# CHECK: c %r4, 0(%r3)
# CHECK: jge [[LABEL:\.L[^ ]*]]
# CHECK: c %r4, 4(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 8(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 12(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 16(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 20(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 24(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 28(%r3)
# CHECK: je [[LABEL]]
# ...lots of other blocks...
# CHECK: c %r4, 1004(%r3)
# CHECK: je [[LABEL:\.L[^ ]*]]
# CHECK: c %r4, 1008(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 1012(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 1016(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 1020(%r3)
# CHECK: je [[LABEL]]
# CHECK: c %r4, 1024(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 1028(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 1032(%r3)
# CHECK: jge [[LABEL]]
# CHECK: c %r4, 1036(%r3)
# CHECK: jge [[LABEL]]

blocks = 256 + 4

print 'define void @f1(i8 *%base, i32 *%stop, i32 %limit) {'
print 'entry:'
print '  br label %b0'
print ''

a, b = 1, 1
for i in xrange(blocks):
    a, b = b, a + b
    value = a % 256
    next = 'b{0:d}'.format((i + 1)) if i + 1 < blocks else 'end'
    other = 'end' if 2 * i < blocks else 'b0'
    print 'b{0:d}:'.format(i)
    print '  store volatile i8 {0:d}, i8 *%base'.format(value)
    print '  %astop{0:d} = getelementptr i32, i32 *%stop, i64 {1:d}'.format(i, i)
    print '  %acur{0:d} = load i32 , i32 *%astop{1:d}'.format(i, i)
    print '  %atest{0:d} = icmp eq i32 %limit, %acur{1:d}'.format(i, i)
    print '  br i1 %atest{0:d}, label %{1!s}, label %{2!s}'.format(i, other, next)

print ''
print '{0!s}:'.format(next)
print '  ret void'
print '}'
