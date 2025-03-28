from copy import copy
from datetime import timezone

from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Post.models import Question,Answer, Vote
from Post.pagination import CustomPageNumberPagination
from Post.serializers import QuestionSerializer, AnswerSerializer


@api_view(['GET', 'POST'])
def questions_list_and_create(request):
    if request.method == 'GET':
        queryset = Question.objects.all()

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))

        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()

        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)

        sort_by = request.query_params.get('sort_by')
        if sort_by:
            if sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'active':
                queryset = queryset.order_by('-updated_at')
            elif sort_by == 'votes':
                queryset = queryset.order_by('-vote_count')
            elif sort_by == 'unanswered':
                queryset = queryset.filter(answer_count=0).order_by('-created_at')

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = QuestionSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        '''{
              "title": "string",
              "content": "string",
              "tags": ["string"]
        }'''
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','PATCH','DELETE'])
def question_details_edit_delete(request, id):
    if request.method == 'GET':
        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message":"question not found by this id"},status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        """
        {
              "title": "string",
              "content": "string",
              "tags": ["string"]
        }
        """
        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message": "question not found by this id"}, status=status.HTTP_404_NOT_FOUND)


        if question.author != request.user:
            return Response({"message":"you are not the owner"}, status=status.HTTP_401_UNAUTHORIZED)
        new_title = request.data.get('title')
        new_content = request.data.get('content')
        new_tags = request.data.get('tags')

        if new_title and new_title != "" and new_title is not None:
            question.title = new_title
        if new_content and new_content != "" and new_content is not None:
            question.content = new_content
        if new_tags and new_tags != [] and new_tags is not None:
            question.tags = new_tags
        question.save()
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message": "question not found by this id"}, status=status.HTTP_404_NOT_FOUND)


        if question.author != request.user:
            return Response({"message":"you are not the owner"}, status=status.HTTP_401_UNAUTHORIZED)
        question.delete()
        return Response({"message":"question deleted"}, status=status.HTTP_204_NO_CONTENT)



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def question_vote(request,id):
    """
    {
      "vote_type": "upvote" // или "downvote"
    }
    """
    try:
        question = Question.objects.get(id=id)
    except Question.DoesNotExist:
        return Response({"message":"question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    vote_type = request.data.get('vote_type')
    if vote_type not in ['upvote', 'downvote', 'Upvote', 'Downvote']:
        return Response({"message":"invalid vote_type"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        vote = Vote.objects.get(question=question,user=request.user)
        if vote.vote_type == vote_type:
            return Response({"message":"you have already cast this vote"}, status=status.HTTP_409_CONFLICT)
        else:
            old_vote = copy(vote.vote_type)
            vote.vote_type = vote_type
            vote.save()

            if old_vote == "upvote" and vote_type == "downvote":
                question.vote_count -= 2
            elif old_vote == "downvote" and vote_type == "upvote":
                question.vote_count += 2
            question.save()
    except Vote.DoesNotExist:
        Vote.objects.create(question=question, user=request.user, vote_type=vote_type)
        if vote_type == "upvote":
            question.vote_count += 1
        elif vote_type == "downvote":
            question.vote_count -= 1
        question.save()
    serializer = QuestionSerializer(question)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET','POST'])
def answer_list_create(request):
    if request.method == 'GET':
        queryset = Answer.objects.all()
        question_id = request.query_params.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"message": "question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        queryset = queryset.filter(question_id=question_id)
        if request.query_params.get('author'):
            queryset = queryset.filter(author=request.query_params.get('author'))
        sort_by = request.query_params.get('sort_by')
        if sort_by:
            if sort_by == 'votes':
                queryset = queryset.order_by('-votes')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-newest')
            elif sort_by == 'oldest':
                queryset = queryset.order_by('-oldest')

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = AnswerSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        """
            {
            "question_id": "string",
            "content": "string"
            }
        """
        question_id = request.data.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"message": "question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH','DELETE'])
def answer_details_edit_delete(request,id):
    if request.method == 'GET':
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerSerializer(answer)
        return Response(serializer.data,status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if answer.author != request.user:
            return Response({'error':'you are not the owner'}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get('content')
        answer.content = new_content

        answer.save()

        serializer = AnswerSerializer(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if answer.author != request.user:
            return Response({'error':'you are not the owner'}, status=status.HTTP_403_FORBIDDEN)
        answer.delete()
        return Response({"message": "answer deleted"}, status=status.HTTP_204_NO_CONTENT)



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def answer_vote(request,id):
    """
        {
          "vote_type": "upvote" // или "downvote"
        }
        """
    try:
        answer = Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    vote_type = request.data.get('vote_type')
    if vote_type not in ['upvote', 'downvote', 'Upvote', 'Downvote']:
        return Response({"message": "invalid vote_type"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        vote = Vote.objects.get(answer=answer, user=request.user)
        if vote.vote_type == vote_type:
            return Response({"message": "you have already cast this vote"}, status=status.HTTP_409_CONFLICT)
        else:
            old_vote = copy(vote.vote_type)
            vote.vote_type = vote_type
            vote.save()

            if old_vote == "upvote" and vote_type == "downvote":
                answer.vote_count -= 2
            elif old_vote == "downvote" and vote_type == "upvote":
                answer.vote_count += 2
            answer.save()
    except Vote.DoesNotExist:
        Vote.objects.create(answer=answer, user=request.user, vote_type=vote_type)
        if vote_type == "upvote":
            answer.vote_count += 1
        elif vote_type == "downvote":
            answer.vote_count -= 1
        answer.save()
    serializer = AnswerSerializer(answer)
    return Response(serializer.data, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def answer_accept(request, id):
    answer = Answer.objects.get(id=id)
    if answer.author != request.user:
        return Response({'error': 'you are not the owner'}, status=status.HTTP_403_FORBIDDEN)
    answer.is_accepted = True
    answer.save()
    serializer = AnswerSerializer(answer)
    return Response(serializer.data, status=status.HTTP_200_OK)