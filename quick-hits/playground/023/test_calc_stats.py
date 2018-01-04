import calc_stats

user_data = [
    { 'id': 1, 'name': 'Aly', 'email': 'alysivji@gmail.com'},
]

activity_data = [
    { 'id': 65, 'description': 'morning jog', 'distance': 3.1 },
    { 'id': 66, 'description': 'lunch break', 'distance': 1.2 },
    { 'id': 67, 'description': 'weekend long run', 'distance': 6.2 },
    { 'id': 67, 'description': 'night run', 'distance': 2.5 },
]


def load_data(endpoint, *args, **kwargs):
    if 'user' in endpoint:
        return user_data
    elif 'activity' in endpoint:
        return activity_data


def test_motivation_message(mocker):
    # Arrange
    mock_api = mocker.MagicMock(name='api')
    mock_api.get.side_effect = load_data
    mocker.patch('calc_stats.fitness_api', new=mock_api)

    # Act
    result = calc_stats.motivation_message('alysivji@gmail.com')

    # Assert
    assert result == f'Aly has run {3.1 + 1.2 + 6.2 + 2.5} miles'
