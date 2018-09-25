from gym.envs.registration import register


register(
    id='MBRLCartpole-v0',
    entry_point='dmbrl.env.cartpole:CartpoleEnv'
)


register(
    id='MBRLReacher3D-v0',
    entry_point='dmbrl.env.reacher:Reacher3DEnv'
)


register(
    id='MBRLPusher-v0',
    entry_point='dmbrl.env.pusher:PusherEnv'
)


register(
    id='MBRLHalfCheetah-v0',
    entry_point='dmbrl.env.half_cheetah:HalfCheetahEnv'
)

register(
    id='VisibleSwimmer-v2',
    entry_point='dmbrl.env.swimmer:VisibleSwimmerEnv',
    max_episode_steps=1000,
    reward_threshold=360.0,
)

register(
    id='VisibleHalfCheetah-v2',
    entry_point='dmbrl.env.visible_half_cheetah:VisibleHalfCheetahEnv',
    max_episode_steps=1000,
    reward_threshold=4800.0,
)
