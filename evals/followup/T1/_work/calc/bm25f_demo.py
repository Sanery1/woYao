k1 = 1.2
title_tf, body_tf = 1, 2
title_weight, body_weight = 2, 1
# Both fields have their own average length, so each length adjustment is 1.
title_x = title_weight * title_tf
body_x = body_weight * body_tf
def saturate(x):
    return (k1 + 1) * x / (x + k1)
print(f"title_x={title_x}; body_x={body_x}; combined_x={title_x + body_x}")
print(f"combine_then_saturate={saturate(title_x + body_x):.6f}")
print(f"separate_then_sum={saturate(title_x) + saturate(body_x):.6f}")
